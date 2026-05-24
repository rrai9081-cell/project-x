import zipfile
import xml.etree.ElementTree as ET
import sys

def get_docx_text(path):
    try:
        with zipfile.ZipFile(path) as docx:
            tree = ET.XML(docx.read('word/document.xml'))
        text = []
        for node in tree.iter():
            if node.tag.endswith('}t') and node.text:
                text.append(node.text)
        return '\n'.join(text)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    print(get_docx_text(sys.argv[1]))
