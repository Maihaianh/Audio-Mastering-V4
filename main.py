import os
import numpy as np
from scipy.io import wavfile
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from plyer import filechooser

# --- NÚT BẤM CÓ TRẠNG THÁI CHÌM KHI CHỌN (STICKY PRESSED STATE) ---
class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.base_color = [0.25, 0.22, 0.35, 1]
        self.is_toggled = False # Trạng thái giữ chìm
        
        with self.canvas.before:
            self.shadow_color = Color(0, 0, 0, 0.4)
            self.shadow = RoundedRectangle(pos=(self.x, self.y - 4), size=self.size, radius=[8])
            
            self.bg_color = Color(0.25, 0.22, 0.35, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            
            self.border_light = Color(1.0, 1.0, 1.0, 0.25)
            self.line_light = Line(rounded_rectangle=(self.x, self.y + 1, self.width, self.height, 8), width=1.2)
            
            self.border_dark = Color(0, 0, 0, 0.5)
            self.line_dark = Line(rounded_rectangle=(self.x, self.y - 1, self.width, self.height, 8), width=1.2)
            
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        if not self.is_toggled:
            self.rect.pos = self.pos
            self.shadow.pos = (self.x, self.y - 4)
            self.line_light.rounded_rectangle = (self.x, self.y + 1, self.width, self.height, 8)
            self.line_dark.rounded_rectangle = (self.x, self.y - 1, self.width, self.height, 8)
        self.rect.size = self.size
        self.shadow.size = self.size

    def set_color(self, rgba):
        self.base_color = rgba
        if not self.is_toggled:
            self.bg_color.rgba = rgba

    def set_toggled(self, toggled):
        """Thiết lập trạng thái chìm (toggled) hoặc nổi (tự động khi chọn nút khác)"""
        self.is_toggled = toggled
        with self.canvas.before:
            if toggled:
                # Trạng thái chìm xuống (lún sâu, bóng thu nhỏ, viền đảo ngược)
                self.rect.pos = (self.x + 1, self.y - 2)
                self.shadow.pos = (self.x + 1, self.y - 2)
                self.line_light.rounded_rectangle = (self.x + 1, self.y - 1, self.width, self.height, 8)
                self.line_dark.rounded_rectangle = (self.x + 1, self.y - 2, self.width, self.height, 8)
                # Đổi màu nền khi được chọn chìm
                self.bg_color.rgba = (0.9, 0.75, 0.2, 1) 
            else:
                # Trở về trạng thái nổi
                self.rect.pos = self.pos
                self.shadow.pos = (self.x, self.y - 4)
                self.line_light.rounded_rectangle = (self.x, self.y + 1, self.width, self.height, 8)
                self.line_dark.rounded_rectangle = (self.x, self.y - 1, self.width, self.height, 8)
                self.bg_color.rgba = self.base_color


# --- COMPONENT KHUNG THẺ (SECTION CARD) ---
class SectionCard(BoxLayout):
    def __init__(self, app_instance, card_index, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance
        self.card_index = card_index
        self.orientation = 'vertical'
        self.padding = 12
        self.spacing = 10
        self.size_hint_y = None
        self.is_active = False
        
        with self.canvas.before:
            self.bg_color = Color(0.12, 0.1, 0.17, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
            self.border_color = Color(0.28, 0.25, 0.4, 1)
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 12), width=1.2)
            
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, 12)

    def set_active(self, active):
        self.is_active = active
        with self.canvas.before:
            if active:
                self.bg_color.rgba = (0.85, 0.7, 0.15, 1)
                self.border_color.rgba = (1.0, 0.9, 0.3, 1)
            else:
                self.bg_color.rgba = (0.12, 0.1, 0.17, 1)
                self.border_color.rgba = (0.28, 0.25, 0.4, 1)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.app_instance.select_tab(self.card_index, scroll_to_it=False)
        return super().on_touch_down(touch)


# --- BỘ XỬ LÝ MASTERING NGOẠI TUYẾN ---
class MasteringEngine:
    @staticmethod
    def process_audio(input_path, output_path, settings):
        if not os.path.exists(input_path):
            raise FileNotFoundError("Không tìm thấy file đầu vào!")

        sr, data = wavfile.read(input_path)
        
        if data.dtype == np.int16:
            audio = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            audio = data.astype(np.float32) / 2147483648.0
        else:
            audio = data.astype(np.float32)

        if len(audio.shape) == 1:
            audio = np.stack((audio, audio), axis=-1)

        if settings.get('auto_level', True):
            peak_val = np.max(np.abs(audio))
            if peak_val > 0:
                audio = audio / peak_val * 0.85

        mid_gain = 10 ** (settings.get('mid_db', 0.0) / 20.0)
        audio[:, 0] *= mid_gain
        audio[:, 1] *= mid_gain

        comp_ratio = settings.get('compression', 35.0) / 100.0
        if comp_ratio > 0:
            threshold = 0.7 - (comp_ratio * 0.4)
            abs_audio = np.abs(audio)
            mask = abs_audio > threshold
            audio[mask] = np.sign(audio[mask]) * (threshold + (abs_audio[mask] - threshold) / (1.0 + comp_ratio * 2))

        width = settings.get('stereo_width', 100.0) / 100.0
        mid = (audio[:, 0] + audio[:, 1]) * 0.5
        side = (audio[:, 0] - audio[:, 1]) * 0.5
        side *= width
        audio[:, 0] = mid + side
        audio[:, 1] = mid - side

        output_gain = 10 ** (settings.get('output_gain', 0.0) / 20.0)
        audio *= output_gain

        if settings.get('soft_clipper', True):
            audio = np.tanh(audio)
        else:
            audio = np.clip(audio, -0.99, 0.99)

        audio_int24 = np.clip(audio * 8388607.0, -8388608, 8388607).astype(np.int32)
        wavfile.write(output_path, settings.get('sample_rate', 44100), audio_int24)
        return output_path


# --- GIAO DIỆN CHÍNH AM-MHA PRO ---
class AMMHAApp(App):
    def build(self):
        self.title = "AM-MHA Pro Audio Mastering"
        self.input_file = ""
        self.output_file = ""
        self.sound = None
        self.buttons_groups = {} # Phân nhóm các nút để quản lý trạng thái chìm/nổi

        main_layout = BoxLayout(orientation='vertical')
        
        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.bind(scroll_y=self.on_scroll)
        
        self.content = BoxLayout(orientation='vertical', padding=12, spacing=14, size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))

        # --- HEADER ---
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=45)
        header.add_widget(Label(text="[b]AM-MHA[/b]\nAUDIO MASTERING · MHA", markup=True, font_size=15, color=(1,1,1,1), halign='left'))
        header.add_widget(Label(text="● ENGINE READY", font_size=11, color=(0.15, 0.9, 0.4, 1), halign='right'))
        self.content.add_widget(header)

        # --- 1. AUDIO PROJECT ---
        self.card_01 = SectionCard(self, 1, height=210)
        self.card_01.add_widget(Label(text="AUDIO PROJECT", bold=True, color=(0.2, 0.2, 0.2, 1), font_size=13, size_hint_y=None, height=22, halign='left'))
        self.lbl_file = Label(text="Chưa có file âm thanh\nChọn file để bắt đầu mastering", font_size=11, color=(0.3,0.3,0.3,1), size_hint_y=None, height=35)
        self.card_01.add_widget(self.lbl_file)

        btn_choose = RoundedButton(text="+ Chọn file âm thanh (WAV, MP3)", font_size=11, size_hint_y=None, height=42)
        btn_choose.bind(on_press=self.open_file_chooser)
        self.card_01.add_widget(btn_choose)

        preview_box = GridLayout(cols=2, spacing=8, size_hint_y=None, height=40)
        self.btn_orig = RoundedButton(text="▶ Nghe bản gốc", font_size=11)
        self.btn_orig.bind(on_press=lambda x: self.handle_group_button_click('preview_group', self.btn_orig))
        self.btn_orig.bind(on_press=lambda x: self.play_audio(is_mastered=False))
        preview_box.add_widget(self.btn_orig)

        self.btn_master = RoundedButton(text="▶ Nghe bản master", font_size=11)
        self.btn_master.bind(on_press=lambda x: self.handle_group_button_click('preview_group', self.btn_master))
        self.btn_master.bind(on_press=lambda x: self.play_audio(is_mastered=True))
        preview_box.add_widget(self.btn_master)
        
        self.card_01.add_widget(preview_box)
        self.content.add_widget(self.card_01)

        # --- 2. MASTERING PRESET ---
        self.card_02 = SectionCard(self, 2, height=110)
        self.card_02.add_widget(Label(text="MASTERING PRESET", bold=True, color=(0.2, 0.2, 0.2, 1), font_size=13, size_hint_y=None, height=22, halign='left'))
        grid_preset = GridLayout(cols=4, spacing=6, size_hint_y=None, height=40)
        
        self.preset_buttons = []
        for name in ["Balanced", "Modern", "Warm", "Vocal"]:
            btn = RoundedButton(text=name, font_size=11)
            btn.bind(on_press=lambda x, p=name, b=btn: self.handle_preset_click(p, b))
            grid_preset.add_widget(btn)
            self.preset_buttons.append(btn)
        self.card_02.add_widget(grid_preset)
        self.content.add_widget(self.card_02)

        # --- 3. TONE & DYNAMICS ---
        self.card_03 = SectionCard(self, 3, height=310)
        self.card_03.add_widget(Label(text="TONE & DYNAMICS", bold=True, color=(0.2, 0.2, 0.2, 1), font_size=13, size_hint_y=None, height=22, halign='left'))

        self.card_03.add_widget(Label(text="Compression (%): 35", font_size=11, color=(0.2,0.2,0.2,1), size_hint_y=None, height=16))
        self.slider_comp = Slider(min=0, max=100, value=35, size_hint_y=None, height=30)
        self.card_03.add_widget(self.slider_comp)

        self.card_03.add_widget(Label(text="Stereo Width (%): 100", font_size=11, color=(0.2,0.2,0.2,1), size_hint_y=None, height=16))
        self.slider_width = Slider(min=0, max=200, value=100, size_hint_y=None, height=30)
        self.card_03.add_widget(self.slider_width)

        self.card_03.add_widget(Label(text="Output Gain (dB): 0.0", font_size=11, color=(0.2,0.2,0.2,1), size_hint_y=None, height=16))
        self.slider_gain = Slider(min=-12, max=6, value=0, size_hint_y=None, height=30)
        self.card_03.add_widget(self.slider_gain)

        self.switch_auto = Switch(active=True)
        row_auto = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        row_auto.add_widget(Label(text="Auto level / cân bằng âm lượng", font_size=11, color=(0.2,0.2,0.2,1), halign='left'))
        row_auto.add_widget(self.switch_auto)
        self.card_03.add_widget(row_auto)

        self.switch_clipper = Switch(active=True)
        row_clip = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        row_clip.add_widget(Label(text="Soft clipper / hạn chế đỉnh mềm", font_size=11, color=(0.2,0.2,0.2,1), halign='left'))
        row_clip.add_widget(self.switch_clipper)
        self.card_03.add_widget(row_clip)
        self.content.add_widget(self.card_03)

        # --- 4. EXPORT MASTER ---
        self.card_04 = SectionCard(self, 4, height=150)
        self.card_04.add_widget(Label(text="EXPORT MASTER", bold=True, color=(0.2, 0.2, 0.2, 1), font_size=13, size_hint_y=None, height=22, halign='left'))
        
        self.lbl_status = Label(text="Sẵn sàng render ngoại tuyến chất lượng cao.", font_size=11, color=(0.2,0.4,0.2,1), size_hint_y=None, height=24)
        self.card_04.add_widget(self.lbl_status)

        btn_export = RoundedButton(text="↓ EXPORT MASTERED AUDIO (WAV 24-bit)", font_size=11, size_hint_y=None, height=48)
        btn_export.bind(on_press=self.start_mastering_export)
        self.card_04.add_widget(btn_export)
        
        self.content.add_widget(self.card_04)

        self.scroll.add_widget(self.content)
        main_layout.add_widget(self.scroll)

        # --- BOTTOM NAVIGATION BAR ---
        nav_bar = GridLayout(cols=4, size_hint_y=None, height=55)
        
        self.nav_buttons = {}
        for idx, name in [(1, "PROJECT"), (2, "PRESETS"), (3, "TOOLS"), (4, "EXPORT")]:
            btn = RoundedButton(text=name, font_size=10)
            btn.bind(on_press=lambda x, i=idx: self.select_tab(i, scroll_to_it=True))
            nav_bar.add_widget(btn)
            self.nav_buttons[idx] = btn

        main_layout.add_widget(nav_bar)

        Clock.schedule_once(lambda dt: self.select_tab(1, scroll_to_it=False), 0.1)
        return main_layout

    def handle_group_button_click(self, group_name, clicked_btn):
        """Quản lý nhóm nút bấm: nút được chọn sẽ chìm xuống, các nút khác nổi lên"""
        if group_name not in self.buttons_groups:
            self.buttons_groups[group_name] = []
        
        # Lấy tất cả nút trong nhóm (ví dụ: nút nghe bản gốc & bản master)
        group_btns = [self.btn_orig, self.btn_master]
        for b in group_btns:
            if b == clicked_btn:
                b.set_toggled(True)
            else:
                b.set_toggled(False)

    def handle_preset_click(self, preset_name, clicked_btn):
        for b in self.preset_buttons:
            if b == clicked_btn:
                b.set_toggled(True)
            else:
                b.set_toggled(False)
        self.apply_preset(preset_name)

    def select_tab(self, tab_index, scroll_to_it=True):
        cards = {1: self.card_01, 2: self.card_02, 3: self.card_03, 4: self.card_04}

        for idx, card in cards.items():
            card.set_active(idx == tab_index)

        for idx, btn in self.nav_buttons.items():
            if idx == tab_index:
                btn.set_toggled(True) # Tab đang chọn chìm xuống
            else:
                btn.set_toggled(False) # Tab khác nổi lên

        if scroll_to_it:
            target_card = cards[tab_index]
            Clock.schedule_once(lambda dt: self.scroll_to_card(target_card), 0.05)

    def on_scroll(self, scrollview, value):
        current_scroll = scrollview.scroll_y
        active_idx = 1
        if current_scroll < 0.25:
            active_idx = 4
        elif current_scroll < 0.5:
            active_idx = 3
        elif current_scroll < 0.8:
            active_idx = 2

        cards = {1: self.card_01, 2: self.card_02, 3: self.card_03, 4: self.card_04}
        for idx, card in cards.items():
            card.set_active(idx == active_idx)

        for idx, btn in self.nav_buttons.items():
            if idx == active_idx:
                btn.set_toggled(True)
            else:
                btn.set_toggled(False)

    def scroll_to_card(self, card):
        try:
            card_y = card.y
            total_height = self.content.height
            scroll_y = 1.0 - (abs(card_y) / max(1, total_height - self.scroll.height))
            self.scroll.scroll_y = max(0.0, min(1.0, scroll_y))
        except Exception as e:
            print("Lỗi cuộn màn hình:", e)

    def open_file_chooser(self, instance):
        filechooser.open_file(on_selection=self.handle_file_selection)

    def handle_file_selection(self, selection):
        if selection:
            self.input_file = selection[0]
            self.lbl_file.text = f"File: {os.path.basename(self.input_file)}"
            self.prepare_preview_master()

    def prepare_preview_master(self):
        try:
            settings = {
                'auto_level': self.switch_auto.active,
                'compression': self.slider_comp.value,
                'stereo_width': self.slider_width.value,
                'output_gain': self.slider_gain.value,
                'soft_clipper': self.switch_clipper.active,
                'sample_rate': 44100
            }
            output_dir = os.path.dirname(self.input_file)
            self.output_file = os.path.join(output_dir, "preview_temp_master.wav")
            MasteringEngine.process_audio(self.input_file, self.output_file, settings)
        except Exception as e:
            print("Lỗi tạo preview:", e)

    def play_audio(self, is_mastered):
        if not self.input_file:
            self.lbl_status.text = "Lỗi: Vui lòng chọn file âm thanh trước!"
            return

        if self.sound:
            self.sound.stop()

        target_file = self.output_file if is_mastered else self.input_file
        
        if is_mastered and not os.path.exists(target_file):
            self.prepare_preview_master()

        self.sound = SoundLoader.load(target_file)
        if self.sound:
            self.sound.play()
            mode_name = "Bản Master (Đã xử lý)" if is_mastered else "Bản Gốc (Original)"
            self.lbl_status.text = f"Đang phát: {mode_name}"
        else:
            self.lbl_status.text = "Không thể phát file âm thanh này."

    def apply_preset(self, preset_name):
        if preset_name == "Balanced":
            self.slider_comp.value = 30
            self.slider_width.value = 100
        elif preset_name == "Modern":
            self.slider_comp.value = 60
            self.slider_width.value = 120
        elif preset_name == "Warm":
            self.slider_comp.value = 25
            self.slider_width.value = 90
        elif preset_name == "Vocal":
            self.slider_comp.value = 40
            self.slider_width.value = 110
        self.lbl_status.text = f"Đã áp dụng Preset: {preset_name}"
        if self.input_file:
            self.prepare_preview_master()

    def start_mastering_export(self, instance):
        if not self.input_file:
            self.lbl_status.text = "Lỗi: Vui lòng chọn file âm thanh trước!"
            return
        self.lbl_status.text = "Đang xử lý xuất file mastering chuyên nghiệp..."
        Clock.schedule_once(self.process_export_task, 0.1)

    def process_export_task(self, dt):
        try:
            settings = {
                'auto_level': self.switch_auto.active,
                'compression': self.slider_comp.value,
                'stereo_width': self.slider_width.value,
                'output_gain': self.slider_gain.value,
                'soft_clipper': self.switch_clipper.active,
                'sample_rate': 44100
            }
            output_dir = os.path.dirname(self.input_file)
            final_output = os.path.join(output_dir, "AM_MHA_Final_Mastered.wav")
            MasteringEngine.process_audio(self.input_file, final_output, settings)
            self.lbl_status.text = f"Thành công! Đã lưu: {os.path.basename(final_output)}"
        except Exception as e:
            self.lbl_status.text = f"Lỗi xuất file: {str(e)}"

if __name__ == '__main__':
    AMMHAApp().run()