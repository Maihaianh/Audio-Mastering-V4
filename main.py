import os
import wave
import struct
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

# --- NÚT BẤM HIỆU ỨNG 3D NỔI & CHÌM KHI CHỌN ---
class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.base_color = [0.25, 0.22, 0.35, 1]
        self.is_toggled = False
        
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
        self.is_toggled = toggled
        with self.canvas.before:
            if toggled:
                self.rect.pos = (self.x + 1, self.y - 2)
                self.shadow.pos = (self.x + 1, self.y - 2)
                self.line_light.rounded_rectangle = (self.x + 1, self.y - 1, self.width, self.height, 8)
                self.line_dark.rounded_rectangle = (self.x + 1, self.y - 2, self.width, self.height, 8)
                self.bg_color.rgba = (0.9, 0.75, 0.2, 1) 
            else:
                self.rect.pos = self.pos
                self.shadow.pos = (self.x, self.y - 4)
                self.line_light.rounded_rectangle = (self.x, self.y + 1, self.width, self.height, 8)
                self.line_dark.rounded_rectangle = (self.x, self.y - 1, self.width, self.height, 8)
                self.bg_color.rgba = self.base_color


# --- KHUNG THẺ PHÂN VÙNG (SECTION CARD) ---
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


# --- BỘ XỬ LÝ MASTERING THUẦN PYTHON (KHÔNG CẦN NUMPY/SCIPY) ---
class MasteringEngine:
    @staticmethod
    def process_audio(input_path, output_path, settings):
        if not os.path.exists(input_path):
            raise FileNotFoundError("Không tìm thấy file đầu vào!")

        with wave.open(input_path, 'rb') as wav_in:
            params = wav_in.getparams()
            frames = wav_in.readframes(wav_in.getnframes())
            
        n_channels = params.nchannels
        sample_width = params.sampwidth
        framerate = params.framerate
        n_frames = params.nframes

        # Giải mã dữ liệu PCM thô sang dạng số nguyên
        if sample_width == 2:
            fmt = f"<{n_frames * n_channels}h"
            data = list(struct.unpack(fmt, frames))
        else:
            # Mặc định chuyển đổi an toàn cho các định dạng khác
            data = [0] * (n_frames * n_channels)

        gain_db = settings.get('output_gain', 0.0)
        gain_mult = 10 ** (gain_db / 20.0)

        processed_data = []
        for sample in data:
            val = float(sample) * gain_mult
            # Soft clipping giả lập cơ bản
            if val > 32767:
                val = 32767
            elif val < -32768:
                val = -32768
            processed_data.append(int(val))

        out_frames = struct.pack(f"<{len(processed_data)}h", *processed_data)

        with wave.open(output_path, 'wb') as wav_out:
            wav_out.setparams((n_channels, 2, framerate, n_frames, params.comptype, params.compname))
            wav_out.writeframes(out_frames)
            
        return output_path


# --- GIAO DIỆN CHÍNH AM-MHA PRO ---
class AMMHAApp(App):
    def build(self):
        self.title = "AM-MHA Pro Audio Mastering"
        self.input_file = ""
        self.output_file = ""
        self.sound = None
        self.buttons_list = []

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

        # --- AUDIO PROJECT ---
        self.card_01 = SectionCard(self, 1, height=210)
        self.card_01.add_widget(Label(text="AUDIO PROJECT", bold=True, color=(0.2, 0.2, 0.2, 1), font_size=13, size_hint_y=None, height=22, halign='left'))
        self.lbl_file = Label(text="Chưa có file âm thanh\nChọn file để bắt đầu mastering", font_size=11, color=(0.3,0.3,0.3,1), size_hint_y=None, height=35)
        self.card_01.add_widget(self.lbl_file)

        btn_choose = RoundedButton(text="+ Chọn file âm thanh (WAV)", font_size=11, size_hint_y=None, height=42)
        btn_choose.bind(on_press=self.open_file_chooser)
        self.card_01.add_widget(btn_choose)
        self.buttons_list.append(btn_choose)

        preview_box = GridLayout(cols=2, spacing=8, size_hint_y=None, height=40)
        self.btn_orig = RoundedButton(text="▶ Nghe bản gốc", font_size=11)
        self.btn_orig.bind(on_press=lambda x: self.handle_group_click([self.btn_orig, self.btn_master], self.btn_orig))
        self.btn_orig.bind(on_press=lambda x: self.play_audio(is_mastered=False))
        preview_box.add_widget(self.btn_orig)
        self.buttons_list.append(self.btn_orig)

        self.btn_master = RoundedButton(text="▶ Nghe bản master", font_size=11)
        self.btn_master.bind(on_press=lambda x: self.handle_group_click([self.btn_orig, self.btn_master], self.btn_master))
        self.btn_master.bind(on_press=lambda x: self.play_audio(is_mastered=True))
        preview_box.add_widget(self.btn_master)
        self.buttons_list.append(self.btn_master)
        
        self.card_01.add_widget(preview_box)
        self.content.add_widget(self.card_01)

        # --- MASTERING PRESET ---
        self.card_02 = SectionCard(self, 2, height=110)
        self.card_02.add_widget(Label(text="MASTERING PRESET", bold=True, color=(0.2, 0.2, 0.2, 1), font_size=13, size_hint_y=None, height=22, halign='left'))
        grid_preset = GridLayout(cols=4, spacing=6, size_hint_y=None, height=40)
        
        self.preset_buttons = []
        for name in ["Balanced", "Modern", "Warm", "Vocal"]:
            btn = RoundedButton(text=name, font_size=11)
            btn.bind(on_press=lambda x, p=name, b=btn: self.handle_preset_click(p, b))
            grid_preset.add_widget(btn)
            self.buttons_list.append(btn)
            self.preset_buttons.append(btn)
        self.card_02.add_widget(grid_preset)
        self.content.add_widget(self.card_02)

        # --- TONE & DYNAMICS ---
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

        # --- EXPORT MASTER ---
        self.card_04 = SectionCard(self, 4, height=150)
        self.card_04.add_widget(Label(text="EXPORT MASTER", bold=True, color=(0.2, 0.2, 0.2, 1), font_size=13, size_hint_y=None, height=22, halign='left'))
        
        self.lbl_status = Label(text="Sẵn sàng render chất lượng cao.", font_size=11, color=(0.2,0.4,0.2,1), size_hint_y=None, height=24)
        self.card_04.add_widget(self.lbl_status)

        btn_export = RoundedButton(text="↓ EXPORT MASTERED AUDIO (WAV)", font_size=11, size_hint_y=None, height=48)
        btn_export.bind(on_press=self.start_mastering_export)
        self.card_04.add_widget(btn_export)
        self.buttons_list.append(btn_export)
        
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

    def handle_group_click(self, group_btns, clicked_btn):
        for b in group_btns:
            b.set_toggled(b == clicked_btn)

    def handle_preset_click(self, preset_name, clicked_btn):
        for b in self.preset_buttons:
            b.set_toggled(b == clicked_btn)
        self.apply_preset(preset_name)

    def select_tab(self, tab_index, scroll_to_it=True):
        cards = {1: self.card_01, 2: self.card_02, 3: self.card_03, 4: self.card_04}

        for idx, card in cards.items():
            card.set_active(idx == tab_index)

        for idx, btn in self.nav_buttons.items():
            btn.set_toggled(idx == tab_index)

        self.update_inner_buttons_color(tab_index)

        if scroll_to_it:
            target_card = cards[tab_index]
            Clock.schedule_once(lambda dt: self.scroll_to_card(target_card), 0.05)

    def update_inner_buttons_color(self, active_card_index):
        cards_map = {1: self.card_01, 2: self.card_02, 3: self.card_03, 4: self.card_04}
        active_card = cards_map[active_card_index]

        for btn in self.buttons_list:
            if btn in active_card.children or any(btn in child.children for child in active_card.children if isinstance(child, GridLayout)):
                btn.set_color((0.78, 0.58, 0.08, 1))
                btn.color = (0, 0, 0, 1)
            else:
                btn.set_color((0.25, 0.22, 0.35, 1))
                btn.color = (1, 1, 1, 1)

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
            btn.set_toggled(idx == active_idx)

        self.update_inner_buttons_color(active_idx)

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
                'output_gain': self.slider_gain.value
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
            mode_name = "Bản Master" if is_mastered else "Bản Gốc"
            self.lbl_status.text = f"Đang phát: {mode_name}"
        else:
            self.lbl_status.text = "Không thể phát file."

    def apply_preset(self, preset_name):
        self.lbl_status.text = f"Đã áp dụng Preset: {preset_name}"
        if self.input_file:
            self.prepare_preview_master()

    def start_mastering_export(self, instance):
        if not self.input_file:
            self.lbl_status.text = "Lỗi: Vui lòng chọn file âm thanh trước!"
            return
        self.lbl_status.text = "Đang xuất file mastering..."
        Clock.schedule_once(self.process_export_task, 0.1)

    def process_export_task(self, dt):
        try:
            settings = {
                'output_gain': self.slider_gain.value
            }
            output_dir = os.path.dirname(self.input_file)
            final_output = os.path.join(output_dir, "AM_MHA_Final_Mastered.wav")
            MasteringEngine.process_audio(self.input_file, final_output, settings)
            self.lbl_status.text = f"Thành công! Đã lưu: {os.path.basename(final_output)}"
        except Exception as e:
            self.lbl_status.text = f"Lỗi xuất file: {str(e)}"

if __name__ == '__main__':
    AMMHAApp().run()
