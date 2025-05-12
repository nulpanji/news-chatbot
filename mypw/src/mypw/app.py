"""
pw reminder
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import os
import json
from cryptography.fernet import Fernet
import random
import string
from datetime import datetime


DATA_FILE = os.path.expanduser('~/.mypw_data.enc')
KEY_FILE = os.path.expanduser('~/.mypw_key')

class 비번관리(toga.App):
    def _get_fernet(self):
        # 암호화 키 파일이 없으면 생성
        if not os.path.exists(KEY_FILE):
            key = Fernet.generate_key()
            with open(KEY_FILE, 'wb') as f:
                f.write(key)
        else:
            with open(KEY_FILE, 'rb') as f:
                key = f.read()
        return Fernet(key)

    def _save_data(self):
        f = self._get_fernet()
        try:
            data = json.dumps(self.pw_list).encode('utf-8')
            enc = f.encrypt(data)
            with open(DATA_FILE, 'wb') as fp:
                fp.write(enc)
        except Exception as e:
            print('저장 오류:', e)

    def _load_data(self):
        f = self._get_fernet()
        if not os.path.exists(DATA_FILE):
            return []
        try:
            with open(DATA_FILE, 'rb') as fp:
                enc = fp.read()
            data = f.decrypt(enc)
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            print('불러오기 오류:', e)
            return []

    def startup(self):
        self.pw_list = self._load_data()  # 암호화 파일에서 불러오기
        self.master_password = "1234"  # 임시 마스터 패스워드
        self.is_authenticated = False
        self.languages = {
            'ko': {
                'app_title': '비밀번호 관리 앱',
                'login': '로그인',
                'pw_placeholder': '마스터 패스워드 입력',
                'pw_wrong': '패스워드가 올바르지 않습니다.',
                'main_title': '비밀번호 관리',
                'site': '사이트명',
                'user_id': '아이디',
                'password': '비밀번호',
                'add': '추가',
                'saved': '저장되었습니다.',
                'fill_all': '모든 항목을 입력하세요.',
                'lang_select': '언어 선택',
                'pw_generate': '자동 생성',
                'pw_upper': '대문자 포함',
                'pw_special': '특수문자 포함',
                'pw_length': '길이',
                'pw_include_birthday': '생년월일 포함',
                'pw_include_phone': '전화번호 포함',
                'pw_include_id': 'ID 포함',
                'birthday': '생년월일(YYYYMMDD)',
                'phone': '전화번호',
                'identification': 'ID',
                'pw_show': '비밀번호 보기',
                'pw_show_title': '비밀번호 표시',
                'pw_show_input': '마스터 패스워드 입력',
                'pw_show_confirm': '확인',
                'pw_show_cancel': '취소',
                'pw_show_error': '비밀번호가 올바르지 않습니다.',
                'pw_created_at': '생성일'
            },
            'en': {
                'app_title': 'Password Manager',
                'login': 'Login',
                'pw_placeholder': 'Enter master password',
                'pw_wrong': 'Password is incorrect.',
                'main_title': 'Password Management',
                'site': 'Site',
                'user_id': 'User ID',
                'password': 'Password',
                'add': 'Add',
                'saved': 'Saved.',
                'fill_all': 'Please fill all fields.',
                'lang_select': 'Language',
                'pw_generate': 'Generate',
                'pw_upper': 'Include Uppercase',
                'pw_special': 'Include Special',
                'pw_length': 'Length',
                'pw_include_birthday': 'Include Birthday',
                'pw_include_phone': 'Include Phone',
                'pw_include_id': 'Include ID',
                'birthday': 'Birthday (YYYYMMDD)',
                'phone': 'Phone',
                'identification': 'ID',
                'pw_show': 'Show Password',
                'pw_show_title': 'Show Password',
                'pw_show_input': 'Enter master password',
                'pw_show_confirm': 'Confirm',
                'pw_show_cancel': 'Cancel',
                'pw_show_error': 'Password is incorrect.',
                'pw_created_at': 'Created at'
            },
            'zh': {
                'app_title': '密码管理器',
                'login': '登录',
                'pw_placeholder': '输入主密码',
                'pw_wrong': '密码不正确。',
                'main_title': '密码管理',
                'site': '网站',
                'user_id': '账号',
                'password': '密码',
                'add': '添加',
                'saved': '已保存。',
                'fill_all': '请填写所有项目。',
                'lang_select': '语言选择',
                'pw_generate': '自动生成',
                'pw_upper': '包含大写字母',
                'pw_special': '包含特殊字符',
                'pw_length': '长度',
                'pw_include_birthday': '包含生日',
                'pw_include_phone': '包含电话',
                'pw_include_id': '包含ID',
                'birthday': '生日(YYYYMMDD)',
                'phone': '电话',
                'identification': 'ID',
                'pw_show': '显示密码',
                'pw_show_title': '显示密码',
                'pw_show_input': '输入主密码',
                'pw_show_confirm': '确认',
                'pw_show_cancel': '取消',
                'pw_show_error': '密码不正确。',
                'pw_created_at': '生成时间'
            }
        }
        self.lang_label_to_code = {'한국어': 'ko', 'English': 'en', '中文': 'zh'}
        self.lang_code_to_label = {v: k for k, v in self.lang_label_to_code.items()}
        self.current_lang = 'ko'
        self._build_login_screen()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.login_box
        self.main_window.show()

    def _build_login_screen(self):
        lang = self.languages[self.current_lang]
        self.login_input = toga.PasswordInput(placeholder=lang['pw_placeholder'])
        self.login_message = toga.Label("")
        login_button = toga.Button(lang['login'], on_press=self._check_password)
        self.lang_select = toga.Selection(
            items=['한국어', 'English', '中文'],
            on_select=self._change_language,
            style=Pack(padding_bottom=10, width=120)
        )
        # 현재 언어 선택 반영 (라벨로 지정)
        self.lang_select.value = self.lang_code_to_label[self.current_lang]

        self.login_title = toga.Label(lang['app_title'], style=Pack(padding=(0, 0, 10, 0), font_size=18))
        self.login_box = toga.Box(
            children=[
                toga.Label(lang['lang_select']),
                self.lang_select,
                self.login_title,
                self.login_input,
                login_button,
                self.login_message
            ],
            style=Pack(direction=COLUMN, alignment="center", padding=30, width=320, height=250)
        )

    def _change_language(self, widget):
        # 언어 변경 시 무한 재귀 방지
        if hasattr(self, '_language_changing') and self._language_changing:
            return
            
        self._language_changing = True
        try:
            selected_label = widget.value
            self.current_lang = self.lang_label_to_code[selected_label]
            
            # 언어 변경 후 UI 재구성
            if self.is_authenticated:
                # 기존 생성일 정보 저장
                date_str = ""
                if hasattr(self, 'pw_created_label') and self.pw_created_label.text:
                    import re
                    m = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', self.pw_created_label.text)
                    if m:
                        date_str = m.group(0)
                
                # 테이블 데이터 백업 - ListSource는 copy()를 지원하지 않으므로 원본 데이터 사용
                table_data_backup = self.pw_list.copy() if hasattr(self, 'pw_list') else []
                
                # 메인 화면 재구성
                self._build_main_screen()
                
                # 테이블 데이터 복원
                if hasattr(self, 'pw_list') and table_data_backup:
                    self.pw_list = table_data_backup
                    # 테이블 데이터 갱신 (마스킹 처리)
                    self._refresh_table()
                
                # 생성일 라벨 갱신
                if date_str and hasattr(self, 'pw_created_label'):
                    lang = self.languages[self.current_lang]
                    self.pw_created_label.text = f"{lang['pw_created_at']}: {date_str}"
                    
                # 테이블 헤더는 갱신할 수 없음 (테이블을 새로 생성해야 함)
                # 헤더를 변경하려면 테이블을 새로 생성해야 하지만, 현재 데이터를 유지하기 위해 생략
                    
                # UI 업데이트
                self.main_window.content = self.main_box
            else:
                # 로그인 화면 재구성
                current_login_value = ""
                if hasattr(self, 'login_input'):
                    current_login_value = self.login_input.value
                    
                self._build_login_screen()
                
                if hasattr(self, 'login_input') and current_login_value:
                    self.login_input.value = current_login_value
                    
                self.main_window.content = self.login_box
        finally:
            self._language_changing = False

    def _check_password(self, widget):
        if self.login_input.value == self.master_password:
            self.is_authenticated = True
            self._build_main_screen()
            self.main_window.content = self.main_box
        else:
            self.login_message.text = self.languages[self.current_lang]['pw_wrong']


    def _generate_password(self, length=16, use_upper=True, use_special=True, birthday=None, phone=None, idnum=None):
        # 옵션에 따라 문자셋 결정
        chars = string.ascii_lowercase + string.digits
        if use_upper:
            chars += string.ascii_uppercase
        if use_special:
            chars += '!@#$%^&*()-_=+[]{};:,.<>?'
        # 개인정보 포함 옵션
        info_parts = []
        if birthday:
            info_parts.append(birthday[-4:])  # 생년월일 끝 4자리
        if phone:
            info_parts.append(phone[-4:])     # 전화번호 끝 4자리
        if idnum:
            info_parts.append(idnum[:3])      # ID 앞 3자리
        info_str = ''.join(info_parts)
        remain_len = max(0, length - len(info_str))
        while True:
            pw_core = ''.join(random.choice(chars) for _ in range(remain_len))
            pw = info_str + pw_core
            # 조건: 소문자/숫자 필수, 옵션에 따라 대문자/특수문자 필수
            if (any(c.islower() for c in pw) and any(c.isdigit() for c in pw)
                and (not use_upper or any(c.isupper() for c in pw))
                and (not use_special or any(c in '!@#$%^&*()-_=+[]{};:,.<>?' for c in pw))):
                return pw

    def _build_main_screen(self):
        lang = self.languages[self.current_lang]
        self.site_input = toga.TextInput(placeholder=lang['site'])
        self.id_input = toga.TextInput(placeholder=lang['user_id'])
        self.pw_input = toga.PasswordInput(placeholder=lang['password'], style=Pack(width=180))
        self.pw_show_btn = toga.Button(lang['pw_show'], on_press=self._on_show_password, style=Pack(width=90, padding_left=4))
        self.pw_created_label = toga.Label("")
        # 개인정보 입력 및 포함 옵션
        self.birthday_input = toga.TextInput(placeholder=lang['birthday'], style=Pack(width=120, padding_left=6))
        self.phone_input = toga.TextInput(placeholder=lang['phone'], style=Pack(width=120, padding_left=6))
        self.id_input2 = toga.TextInput(placeholder=lang['identification'], style=Pack(width=120, padding_left=6))
        self.pw_include_birthday = toga.Switch(lang['pw_include_birthday'], style=Pack(padding_left=6))
        self.pw_include_phone = toga.Switch(lang['pw_include_phone'], style=Pack(padding_left=6))
        self.pw_include_id = toga.Switch(lang['pw_include_id'], style=Pack(padding_left=6))
        # 옵션 위젯
        self.pw_upper = toga.Switch(lang['pw_upper'], style=Pack(padding_left=6))
        self.pw_upper.value = True
        self.pw_special = toga.Switch(lang['pw_special'], style=Pack(padding_left=6))
        self.pw_special.value = True
        self.pw_length = toga.NumberInput(min=6, max=32, step=1, value=16, style=Pack(width=60, padding_left=6))
        # 수동 입력 스위치 추가
        self.manual_pw_switch = toga.Switch('수동 입력', value=False, style=Pack(padding_left=6))
        self.manual_pw_switch.on_change = self._on_manual_pw_switch
        self.pw_generate_btn = toga.Button(lang['pw_generate'], on_press=self._on_generate_password, style=Pack(width=80, padding_left=4))
        self.message_label = toga.Label("")
        # 비밀번호는 항상 마스킹(●●●●●●●●)으로 표시
        def mask_pw(pw):
            return '●' * len(pw) if pw else ''
        self.table = toga.Table(
            headings=[lang['site'], lang['user_id'], lang['password']],
            data=[(item['site'], item['user_id'], mask_pw(item['pw'])) for item in self.pw_list],
            style=Pack(flex=1, padding_top=10),
            multiple_select=True,
            on_activate=self._on_table_double_click
        )
        add_button = toga.Button(lang['add'], on_press=self._add_password)
        self.lang_select_main = toga.Selection(
            items=['한국어', 'English', '中文'],
            on_change=self._change_language,
            style=Pack(width=120, padding_bottom=10)
        )
        self.lang_select_main.value = self.lang_code_to_label[self.current_lang]

        pw_opt_box = toga.Box(children=[
            self.pw_upper, self.pw_special, toga.Label(lang['pw_length']), self.pw_length, self.pw_generate_btn, self.manual_pw_switch
        ], style=Pack(direction=ROW, padding_bottom=4))
        # 개인정보 옵션 박스
        info_box = toga.Box(children=[
            self.birthday_input, self.pw_include_birthday,
            self.phone_input, self.pw_include_phone,
            self.id_input2, self.pw_include_id
        ], style=Pack(direction=ROW, padding_bottom=4))
        pw_box = toga.Box(children=[self.pw_input, self.pw_show_btn], style=Pack(direction=ROW))
        pw_created_box = toga.Box(children=[self.pw_created_label], style=Pack(direction=ROW, padding_bottom=4))
        input_box = toga.Box(
            children=[self.site_input, self.id_input, pw_box, add_button],
            style=Pack(direction=ROW, padding_bottom=10)
        )
        # 수정, 삭제 버튼 추가
        self.edit_btn = toga.Button('수정', on_press=self._on_edit_row, style=Pack(width=80, padding_right=8))
        self.delete_btn = toga.Button('삭제', on_press=self._on_delete_row, style=Pack(width=80))
        btn_box2 = toga.Box(children=[self.edit_btn, self.delete_btn], style=Pack(direction=ROW, padding_top=8, padding_bottom=8))
        self.bulk_delete_btn = toga.Button('선택 삭제', on_press=self._on_bulk_delete, style=Pack(width=100, padding_top=4, padding_bottom=4))
        self.site_input.value = ''
        self.user_id_input.value = ''
        self.pw_input.value = ''
        self.message_label.text = ''
        # 편집 모드 해제
        self.edit_mode = False
        self.edit_index = None

    def _on_table_double_click(self, widget, row):
        # 비밀번호 셀 더블클릭 시 마스터 패스워드 인증 후 평문 표시
        if not row:  # 더블클릭에서는 row가 직접 전달됨
            return
        # 테이블에서 더블클릭된 행의 인덱스 찾기
        try:
            selected_index = self.table.data.index(row)
            # 해당 인덱스에 해당하는 항목 가져오기
            pw_item = self.pw_list[selected_index]
        except (ValueError, IndexError):
            # 해당 항목을 찾지 못한 경우
            return
        if pw_item is None:
            return
        real_pw = pw_item['pw']
        # 마스터 패스워드 입력 팝업
        def on_confirm(b):
            if pw_input.value == self.master_password:
                dlg.close()
                # 평문 비밀번호 표시 팝업
                pw_dlg = toga.Window(title=lang['pw_show_title'], size=(350, 120))
                pw_label = toga.Label(real_pw, style=Pack(font_size=16, padding=20))
                pw_dlg.content = pw_label
                pw_dlg.show()
            else:
                err_label.text = lang['pw_show_error']
        def on_cancel(b):
            dlg.close()
        pw_input = toga.PasswordInput(placeholder=lang['pw_show_input'])
        err_label = toga.Label("")
        confirm_btn = toga.Button(lang['pw_show_confirm'], on_press=on_confirm, style=Pack(width=80, padding_right=8))
        cancel_btn = toga.Button(lang['pw_show_cancel'], on_press=on_cancel, style=Pack(width=80))
        btn_box = toga.Box(children=[confirm_btn, cancel_btn], style=Pack(direction=ROW, padding_top=8))
        dlg_box = toga.Box(children=[toga.Label(lang['pw_show_title']), pw_input, err_label, btn_box], style=Pack(direction=COLUMN, padding=16))
        dlg = toga.Window(title=lang['pw_show_title'], size=(320, 180))
        dlg.content = dlg_box
        dlg.show()

    def _on_bulk_delete(self, widget):
        # 테이블의 선택 항목 처리
        selected = self.table.selection
        if not selected:
            self.message_label.text = '삭제할 항목을 선택하세요.'
            return
        # 단일 선택이면 리스트로 변환
        if not isinstance(selected, (list, set)):
            rows = [selected]
        else:
            rows = list(selected)
        # 삭제할 항목들 찾기
        items_to_delete = []
        for row in rows:
            try:
                # 테이블에서 해당 행의 인덱스 찾기
                index = self.table.data.index(row)
                # 해당 인덱스에 있는 항목의 사이트와 아이디 추출
                site = self.pw_list[index]['site']
                user_id = self.pw_list[index]['user_id']
                items_to_delete.append((site, user_id))
            except (ValueError, IndexError):
                # 해당 행을 찾지 못한 경우 무시하고 다음 항목으로 진행
                continue
        # 찾은 항목들 삭제
        for site, user_id in items_to_delete:
            self.pw_list = [item for item in self.pw_list if not (item['site'] == site and item['user_id'] == user_id)]
        self._save_data()
        self._refresh_table()
        self.message_label.text = '선택한 항목들이 삭제되었습니다.'

    def _on_edit_row(self, widget):
        selected = self.table.selection
        if not selected:
            self.message_label.text = '수정할 항목을 선택하세요.'
            return
        # 선택된 행의 인덱스 찾기
        try:
            selected_index = self.table.data.index(selected)
        except ValueError:
            self.message_label.text = '올바른 항목을 찾을 수 없습니다.'
            return
        # pw_list에서 해당 데이터 가져오기
        item = self.pw_list[selected_index]
        self.site_input.value = item['site']
        self.user_id_input.value = item['user_id']
        self.pw_input.value = item['pw']
        self.edit_mode = True
        self.edit_index = selected_index
        self.message_label.text = '항목을 수정 후 저장하세요.'

    def _add_password(self, widget):
        site = self.site_input.value.strip()
        user_id = self.user_id_input.value.strip()
        pw = self.pw_input.value.strip()
        if not site or not user_id or not pw:
            self.message_label.text = '모든 필드를 입력하세요.'
            return
        # 편집 모드일 경우 기존 데이터 수정
        if getattr(self, 'edit_mode', False):
            idx = getattr(self, 'edit_index', None)
            if idx is not None and 0 <= idx < len(self.pw_list):
                self.pw_list[idx] = {'site': site, 'user_id': user_id, 'pw': pw}
                self.edit_mode = False
                self.edit_index = None
                self.message_label.text = '항목이 수정되었습니다.'
            else:
                self.message_label.text = '수정할 항목이 올바르지 않습니다.'
                return
        else:
            # 신규 추가
            self.pw_list.append({'site': site, 'user_id': user_id, 'pw': pw})
            self.message_label.text = '항목이 추가되었습니다.'
        self._refresh_table()

def main():
    return 비번관리()
