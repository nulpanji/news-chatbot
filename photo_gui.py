import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# 중복 탐지 함수
def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicates(folder):
    hashes = {}
    duplicates = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
                path = os.path.join(root, file)
                try:
                    file_hash = get_file_hash(path)
                    if file_hash in hashes:
                        duplicates.append((path, hashes[file_hash]))  # (중복, 원본)
                    else:
                        hashes[file_hash] = path
                except:
                    continue
    return duplicates

# GUI 클래스
class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("중복 사진 탐색기")
        self.folder_path = ""

        # UI 구성
        self.label = tk.Label(root, text="폴더를 선택하세요:")
        self.label.pack(pady=5)

        self.select_button = tk.Button(root, text="📁 폴더 선택", command=self.select_folder)
        self.select_button.pack(pady=3)

        self.find_button = tk.Button(root, text="🔍 중복 검색", command=self.search_duplicates)
        self.find_button.pack(pady=3)

        self.delete_button = tk.Button(root, text="🗑 중복 삭제", command=self.delete_duplicates)
        self.delete_button.pack(pady=3)

        self.result_area = scrolledtext.ScrolledText(root, width=80, height=20)
        self.result_area.pack(pady=10)

        self.duplicates = []

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            self.result_area.insert(tk.END, f"\n✅ 선택된 폴더: {folder}\n")

    def search_duplicates(self):
        if not self.folder_path:
            messagebox.showerror("오류", "먼저 폴더를 선택하세요!")
            return

        self.result_area.delete(1.0, tk.END)
        self.result_area.insert(tk.END, "⏳ 중복 검사 중입니다...\n")
        self.root.update_idletasks()  # UI 강제 갱신

        self.duplicates = find_duplicates(self.folder_path)

        self.result_area.insert(tk.END, "🔁 중복 검사 완료!\n\n")

        if not self.duplicates:
            self.result_area.insert(tk.END, "🎉 중복 사진 없음!\n")
        else:
            self.result_area.insert(tk.END, f"🔁 중복 사진 {len(self.duplicates)}건 발견:\n\n")
            for dup, original in self.duplicates:
                self.result_area.insert(tk.END, f"🧩 {dup}\n↪️ 원본: {original}\n\n")

    def delete_duplicates(self):
        if not self.duplicates:
            messagebox.showinfo("안내", "중복된 파일이 없습니다.")
            return

        deleted = 0
        for dup, _ in self.duplicates:
            try:
                os.remove(dup)
                deleted += 1
            except Exception as e:
                self.result_area.insert(tk.END, f"⚠️ 삭제 실패: {dup}\n")

        messagebox.showinfo("삭제 완료", f"{deleted}개의 중복 파일이 삭제되었습니다.")
        self.result_area.insert(tk.END, f"\n🗑 삭제된 파일 수: {deleted}\n")

# 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()
