import os

# 제외할 폴더/확장자 (필요시 추가)
EXCLUDE_DIRS = ['.git', '.venv', 'venv', '__pycache__', 'node_modules', '.streamlit']
EXCLUDE_EXTS = ['.zip', '.tar', '.tar.gz', '.rar', '.7z', '.db', '.sqlite3', '.xlsx', '.csv', '.jpg', '.png', '.mp4', '.mov', '.avi', '.pdf']
SIZE_LIMIT_MB = 10  # 10MB 이상 파일만 탐색

def find_large_files(root='.'):
    large_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # 제외 폴더
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                if os.path.getsize(fpath) > SIZE_LIMIT_MB * 1024 * 1024:
                    large_files.append(fpath)
                elif any(fname.lower().endswith(ext) for ext in EXCLUDE_EXTS):
                    large_files.append(fpath)
            except Exception:
                continue
    return large_files

def append_to_gitignore(files):
    with open('.gitignore', 'a', encoding='utf-8') as f:
        for file in files:
            rel_path = os.path.relpath(file)
            if rel_path not in open('.gitignore', encoding='utf-8').read():
                f.write(rel_path.replace('\\', '/') + '\n')

def delete_files(files):
    for file in files:
        try:
            os.remove(file)
            print(f'삭제됨: {file}')
        except Exception as e:
            print(f'삭제 실패: {file} ({e})')

if __name__ == '__main__':
    print('대용량/불필요 파일 탐색 중...')
    large_files = find_large_files('.')
    if not large_files:
        print('대용량 파일 없음!')
    else:
        print(f'발견된 파일 {len(large_files)}개:')
        for f in large_files:
            print(' -', f)
        append_to_gitignore(large_files)
        confirm = input('위 파일을 모두 삭제할까요? (y/n): ')
        if confirm.lower() == 'y':
            delete_files(large_files)
        else:
            print('삭제하지 않고 .gitignore에만 추가했습니다.')