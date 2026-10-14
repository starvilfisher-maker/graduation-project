#!/usr/bin/env python3
"""Build local, source-hashed visual QC pages; never claim human review.

Generated panels are scientific annotation overlays, not model predictions.
No raw files or annotations are altered; all output stays in a new directory.
"""

import argparse
import csv
import hashlib
import html
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from breast_unet.data_audit import sha256_file
from breast_unet.preprocessing import POLICY, read_image, read_mask, read_visible_rgb, resize_image, resize_mask


def boundary(mask):
    import numpy as np
    binary = mask.astype(bool)
    padded = np.pad(binary, 1, constant_values=False)
    inside = (padded[:-2, 1:-1] & padded[2:, 1:-1]
              & padded[1:-1, :-2] & padded[1:-1, 2:])
    return binary & ~inside


def overlay(rgb, targets, other):
    import numpy as np
    canvas = np.rint(np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    for mask in other:
        canvas[boundary(mask)] = (50, 210, 255)
    for mask in targets:
        canvas[boundary(mask)] = (255, 194, 45)
    return canvas


def build_review(audit_dir: Path, output_dir: Path):
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont, ImageOps

    audit_dir, output_dir = audit_dir.resolve(), output_dir.resolve()
    audit_dir.relative_to(ROOT)
    output_dir.relative_to(ROOT)
    if output_dir.exists():
        raise FileExistsError("review output exists; choose a new run_id")
    if output_dir.is_relative_to((ROOT / "data/raw").resolve()):
        raise ValueError("review output cannot be inside raw data")
    summary_path = audit_dir / 'audit_summary.json'
    summary = json.loads(summary_path.read_text())
    if not summary['automatic_checks_passed'] or summary.get('decoding_policy') != 'breast_v1':
        raise ValueError("a successful breast_v1 decoding audit is required")
    if summary.get('preprocessing_policy') != POLICY:
        raise ValueError("policy changed since audit; rerun audit first")
    for name, checksum in summary['code_sha256'].items():
        if sha256_file(ROOT / name) != checksum:
            raise ValueError("audited source code changed; rerun audit first")
    for name, checksum in summary['output_sha256'].items():
        if sha256_file(audit_dir / name) != checksum:
            raise ValueError("audit output changed")
    with (audit_dir / 'cases.csv').open(encoding='utf-8-sig', newline='') as f:
        cases = list(csv.DictReader(f))
    with (audit_dir / 'file_inventory.csv').open(encoding='utf-8-sig', newline='') as f:
        inventory = list(csv.DictReader(f))
    for item in inventory:
        path = (ROOT / item['path']).resolve()
        path.relative_to(ROOT)
        if sha256_file(path) != item['sha256']:
            raise ValueError("raw source changed since audit")
    output_dir.mkdir(parents=True)
    (output_dir / 'cases').mkdir()
    (output_dir / 'contacts').mkdir()
    font = ImageFont.load_default(size=18)
    small = ImageFont.load_default(size=14)
    title = ImageFont.load_default(size=23)
    cards, review_rows, near_vectors = [], [], []
    for row in cases:
        image_path = ROOT / json.loads(row['image_paths'])[0]
        target_paths = [ROOT / p for p in json.loads(row['tumor_paths'])]
        other_paths = [ROOT / p for p in json.loads(row['other_paths'])]
        visible = read_visible_rgb(image_path)
        gray = read_image(image_path)
        targets, other = [read_mask(p) for p in target_paths], [read_mask(p) for p in other_paths]
        tiny = resize_image(gray)
        resized_rgb = np.repeat(tiny[..., None], 3, axis=2)
        panels = [
            Image.fromarray(np.rint(visible*255).astype(np.uint8)),
            Image.fromarray(overlay(visible, targets, other)),
            Image.fromarray(overlay(resized_rgb, [resize_mask(m) for m in targets], [resize_mask(m) for m in other])),
        ]
        canvas = Image.new('RGB', (1224, 558), '#F5F7FA')
        draw = ImageDraw.Draw(canvas)
        draw.text((20, 14), f"{row['image_id']} | {row['classification']} | original {row['width']} x {row['height']}", font=title, fill='#162436')
        labels = ['Visible source (black alpha background)', 'Native reference contour', '256 x 256 grayscale + reference']
        for idx, (panel, label) in enumerate(zip(panels, labels)):
            x = 20 + idx*402
            draw.text((x, 52), label, font=small, fill='#162436')
            box = Image.new('RGB', (380, 380), 'black')
            # Aspect-preserving display only. Model input is direct 256x256.
            shown = ImageOps.contain(panel, (380, 380), Image.Resampling.NEAREST if idx == 2 else Image.Resampling.BILINEAR)
            box.paste(shown, ((380-shown.width)//2, (380-shown.height)//2))
            canvas.paste(box, (x, 80))
        flags = json.loads(row['review_flags'])
        draw.text((20, 475), f"Target pixels: native={row['target_area_px'] or 'none'}; 256={row['target_area_px_256'] or 'none'} | Flags: {', '.join(flags) or 'none'}", font=font, fill='#162436')
        draw.text((20, 506), 'Yellow: expert tumor | Cyan: other (not target) | No model predictions | TCIA BrEaST v1, CC BY 4.0', font=small, fill='#48546A')
        canvas.save(output_dir / 'cases' / (row['image_id']+'.png'))
        # Compact native contour contact card; detailed panels remain available.
        card = Image.new('RGB', (350, 350), '#F5F7FA')
        d = ImageDraw.Draw(card)
        d.text((8, 5), row['image_id']+'  '+row['classification'], fill='#162436', font=font)
        preview = ImageOps.contain(panels[1], (334, 290), Image.Resampling.BILINEAR)
        card.paste(preview, ((350-preview.width)//2, 33+(290-preview.height)//2))
        d.text((8, 328), f"256 target px: {row['target_area_px_256'] or 'none'}"+(' | EDGE' if flags else ''), font=small, fill='#162436')
        cards.append(card)
        tags = []
        if row['classification'] == 'normal': tags.append('normal')
        if int(row['image_alpha_zero_pixels'] or 0): tags.append('alpha')
        if row['image_rgb_equal'] == 'False': tags.append('color')
        if other_paths: tags.append('other')
        if flags: tags.append('flag')
        if row['target_area_px_256'] and int(row['target_area_px_256']) < 600: tags.append('small_review')
        review_rows.append({'case_id': row['image_id'], 'classification': row['classification'], 'tags': tags,
                            'automatic_flags': flags, 'panel': 'cases/'+row['image_id']+'.png',
                            'assistant_visual_review': 'not_yet_reviewed', 'human_review': 'pending'})
        low = np.asarray(Image.fromarray(gray).resize((64, 64), Image.Resampling.BILINEAR)).ravel()
        near_vectors.append(low)
    page_count = (len(cards)+15)//16
    for index in range(page_count):
        sheet = Image.new('RGB', (1440, 1460), '#E5EAF0')
        ImageDraw.Draw(sheet).text((16, 10), f"BrEaST reference QC | page {index+1}/{page_count} | yellow=tumor, cyan=other | not predictions", font=font, fill='#162436')
        for slot, card in enumerate(cards[index*16:(index+1)*16]):
            sheet.paste(card, (10+(slot%4)*356, 44+(slot//4)*352))
        sheet.save(output_dir/'contacts'/f'page_{index+1:02d}.png')
    # Exploratory duplicate triage only. Never excludes or merges patients.
    matrix = np.asarray(near_vectors, dtype=np.float64)
    centered = matrix-matrix.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(centered, axis=1, keepdims=True)
    normalized = np.divide(centered, norms, out=np.zeros_like(centered), where=norms > 0)
    correlations = normalized @ normalized.T
    similar = []
    for i in range(len(cases)):
        for j in range(i+1, len(cases)):
            if correlations[i, j] >= .985:
                mae = float(np.mean(np.abs(matrix[i]-matrix[j])))
                if mae <= .05:
                    similar.append({'first': cases[i]['image_id'], 'second': cases[j]['image_id'],
                                    'correlation': float(correlations[i,j]), 'mean_absolute_difference': mae})
    result = {'source_audit': audit_dir.relative_to(ROOT).as_posix(),
              'source_audit_sha256': sha256_file(summary_path),
              'case_panels': len(cases), 'contact_pages': page_count,
              'generated_panels_are_not_review_completion': True,
              'preprocessing_policy': POLICY, 'cases': review_rows,
              'near_duplicate_triage': {'method': '64x64 grayscale Pearson >=0.985 and MAE <=0.05; no automatic exclusion',
                                        'pairs': similar, 'does_not_prove_absence_of_all_duplicates': True},
              'generator_sha256': sha256_file(Path(__file__))}
    (output_dir/'review_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    items = '\n'.join(f'<a class="card" data-tags="{html.escape(" ".join(r["tags"]))}" href="{r["panel"]}" target="_blank"><img loading="lazy" src="{r["panel"]}" alt="{r["case_id"]}"><b>{r["case_id"]}</b> {r["classification"]}<span>{html.escape(", ".join(r["tags"]) or "常规检查")}</span></a>' for r in review_rows)
    page_links = ' '.join(f'<a href="contacts/page_{i:02d}.png" target="_blank">第{i}页</a>' for i in range(1,page_count+1))
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BrEaST 数据核对图册</title><style>
    body{font:16px/1.6 system-ui,sans-serif;background:#f4f6fa;color:#172536;max-width:1280px;margin:32px auto;padding:0 24px}h1{font-size:28px}p{max-width:960px}nav{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}button{padding:8px 16px;border:1px solid #93a5bb;border-radius:6px;background:white;cursor:pointer}button.active{background:#173e63;color:white}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px}.card{color:inherit;text-decoration:none;background:white;border:1px solid #d8e1eb;border-radius:10px;overflow:hidden;padding:12px}.card img{width:100%}.card span{display:block;color:#52647a}.pages a{display:inline-block;margin:4px 12px 4px 0}a{color:#24577c}small{color:#53677c}</style>
    <h1>BrEaST 数据核对图册</h1><p>共256例。每幅三联图依次显示：按透明度合成的原始显示、专家轮廓、256×256灰度输入与参考轮廓。黄色为目标病灶，青色为other，均不是模型预测。点击图片查看大图。</p>
    <p>原始显示与专家轮廓面板保持原图宽高比；第三面板体现统一正方形输入。图册生成不等于核对完成，审阅记录单独保存。small_review仅是小面积图像复查标签（小于600像素），不作为正式病灶大小分组。</p>
    <nav><button class="active" data-filter="">全部</button><button data-filter="flag">自动提示</button><button data-filter="alpha">原图透明区</button><button data-filter="color">颜色通道不同</button><button data-filter="other">有other标注</button><button data-filter="normal">正常病例</button><button data-filter="small_review">较小目标复查</button></nav><p id="count"></p><section>ITEMS</section><p class="pages">总览联系表：PAGES</p><p><small>来源：<a href="https://www.cancerimagingarchive.net/collection/breast-lesions-usg/">TCIA Breast-Lesions-USG</a>；<a href="https://doi.org/10.1038/s41597-024-02984-z">Pawłowska 等，2024</a>；CC BY 4.0。所有图片仅保存在本地。</small></p>
    <script>const cards=[...document.querySelectorAll('.card')];document.querySelectorAll('button').forEach(b=>b.onclick=()=>{document.querySelectorAll('button').forEach(x=>x.classList.remove('active'));b.classList.add('active');let n=0;cards.forEach(c=>{let show=!b.dataset.filter||c.dataset.tags.split(' ').includes(b.dataset.filter);c.style.display=show?'block':'none';if(show)n++});document.getElementById('count').textContent='当前显示 '+n+' 例';});document.querySelector('button').click();</script></html>'''.replace('ITEMS',items).replace('PAGES',page_links)
    (output_dir/'index.html').write_text(page,encoding='utf-8')
    print(json.dumps({'panels':len(cases),'pages':page_count,'near_duplicate_candidates':len(similar),
                      'output':output_dir.relative_to(ROOT).as_posix()},ensure_ascii=False))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-dir',required=True)
    parser.add_argument('--output-dir',required=True)
    args=parser.parse_args()
    build_review(ROOT/args.audit_dir,ROOT/args.output_dir)
