"""
将测试语料的文本文件转换为 PDF 文件
用于本地测试知识库上传功能
"""
import fitz  # PyMuPDF
from pathlib import Path
import re


def text_to_pdf(txt_path: Path, output_path: Path):
    """将文本文件转换为 PDF"""
    text = txt_path.read_text(encoding="utf-8")

    # 从文件名提取论文标题
    filename = txt_path.stem
    parts = filename.split("_", 1)
    paper_id = parts[0] if len(parts) > 0 else filename
    paper_title = parts[1].replace("_", " ") if len(parts) > 1 else filename

    # 创建 PDF
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4

    # 边距
    margin_x = 50
    margin_y = 50
    max_width = 595 - 2 * margin_x
    line_height = 14

    # 写入标题
    title_fontsize = 16
    page.insert_text(
        (margin_x, margin_y),
        paper_title,
        fontsize=title_fontsize,
        fontname="helv",
    )
    current_y = margin_y + 30

    # 写入 arXiv ID
    page.insert_text(
        (margin_x, current_y),
        f"arXiv:{paper_id}",
        fontsize=10,
        fontname="helv",
    )
    current_y += 20

    # 分割线
    page.draw_line(
        (margin_x, current_y),
        (595 - margin_x, current_y),
        color=(0.5, 0.5, 0.5),
        width=0.5,
    )
    current_y += 15

    # 按段落写入正文
    paragraphs = re.split(r'\n\s*\n', text)

    for para in paragraphs:
        para = para.strip()
        if not para:
            current_y += line_height
            continue

        # 简单的自动换行
        words = para.split()
        line = ""
        for word in words:
            test_line = (line + " " + word).strip()
            # 估算文本宽度（每个字符约 6 像素，12号字）
            if len(test_line) * 6 > max_width:
                if line:
                    if current_y > 842 - margin_y:
                        page = doc.new_page(width=595, height=842)
                        current_y = margin_y
                    page.insert_text(
                        (margin_x, current_y),
                        line,
                        fontsize=11,
                        fontname="helv",
                    )
                    current_y += line_height
                line = word
            else:
                line = test_line

        if line:
            if current_y > 842 - margin_y:
                page = doc.new_page(width=595, height=842)
                current_y = margin_y
            page.insert_text(
                (margin_x, current_y),
                line,
                fontsize=11,
                fontname="helv",
            )
            current_y += line_height

        current_y += 6  # 段落间距

    doc.save(str(output_path))
    doc.close()
    return output_path.stat().st_size


def main():
    test_corpus_dir = Path(__file__).parent / "test_corpus"
    output_dir = Path(__file__).parent / "test_pdfs"
    output_dir.mkdir(exist_ok=True)

    txt_files = sorted(test_corpus_dir.glob("*.txt"))
    print(f"找到 {len(txt_files)} 个文本文件")

    success_count = 0
    for txt_file in txt_files[:10]:  # 只转前10个
        pdf_path = output_dir / (txt_file.stem + ".pdf")
        try:
            size = text_to_pdf(txt_file, pdf_path)
            print(f"✅ {txt_file.name} -> {pdf_path.name} ({size//1024}KB)")
            success_count += 1
        except Exception as e:
            print(f"❌ {txt_file.name}: {e}")

    print(f"\n完成！成功转换 {success_count} 个 PDF")
    print(f"输出目录: {output_dir}")


if __name__ == "__main__":
    main()
