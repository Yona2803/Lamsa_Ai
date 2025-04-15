from customtkinter import CTkImage
from PIL import Image
import os


class ThemeManager:
    def __init__(self, is_dark_mode=True):
        self.is_dark_mode = is_dark_mode
        self.update_theme_colors()

    def define_colors(self):
        # Dark mode colors
        self.dark_PrimaryColor = "#242424"
        self.dark_SecondaryColor = "#2F2F2F"
        self.dark_TertiaryColor_ON = "#4CD951"
        self.dark_TertiaryColor_OFF = "#D94C4E"
        self.dark_Font_Main = "#C8C8C8"
        self.dark_Font_Secondary = "#D0D0D0"
        self.dark_Font_Tertiary = "#F9F7FF"
        self.dark_Active = "#8265FC"
        self.dark_Hover = "#B562E7"
        self.dark_Base = "#424242"
        self.dark_Code_font = "#939DA7"
        self.dark_Code_bg = "#1F2831"

        # Light mode colors
        self.light_PrimaryColor = "#FFFFFF"
        self.light_SecondaryColor = "#FFFFFF"
        self.light_TertiaryColor_ON = "#4CD951"
        self.light_TertiaryColor_OFF = "#D94C4E"
        self.light_Font_Main = "#A6A6A6"
        self.light_Font_Secondary = "#5D5D5D"
        self.light_Font_Tertiary = "#F9F7FF"
        self.light_Active = "#8265FC"
        self.light_Hover = "#B562E7"
        self.light_Base = "#F2F2F2"
        self.light_Code_font = "#052049"
        self.light_Code_bg = "#D7DFE7"

    @staticmethod
    def Icons(name):
        path = f"Assets/Icons/{name}.png"
        if os.path.exists(path):
            return {"icon": CTkImage(Image.open(path), size=(16, 16))}
        # raise FileNotFoundError(f"Icon not found: {path}")

    def update_theme_colors(self):
        self.define_colors()

        if self.is_dark_mode:
            self.primaryColor = self.dark_PrimaryColor
            self.secondaryColor = self.dark_SecondaryColor
            self.tertiaryColor_ON = self.dark_TertiaryColor_ON
            self.tertiaryColor_OFF = self.dark_TertiaryColor_OFF
            self.font_Main = self.dark_Font_Main
            self.font_Secondary = self.dark_Font_Secondary
            self.font_Tertiary = self.dark_Font_Tertiary
            self.base_bg = self.dark_Base
            self.hover_bg = self.dark_Hover
            self.active_bg = self.dark_Active
            self.code_font = self.dark_Code_font
            self.code_bg = self.dark_Code_bg
        else:
            self.primaryColor = self.light_PrimaryColor
            self.secondaryColor = self.light_SecondaryColor
            self.tertiaryColor_ON = self.light_TertiaryColor_ON
            self.tertiaryColor_OFF = self.light_TertiaryColor_OFF
            self.font_Main = self.light_Font_Main
            self.font_Secondary = self.light_Font_Secondary
            self.font_Tertiary = self.light_Font_Tertiary
            self.base_bg = self.light_Base
            self.hover_bg = self.light_Hover
            self.active_bg = self.light_Active
            self.code_font = self.light_Code_font
            self.code_bg = self.light_Code_bg

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.update_theme_colors()
        return self.is_dark_mode

    def get_theme_mode(self):
        return "dark" if self.is_dark_mode else "light"

    def get_theme_icon(self):
        return (
            self.Icons("light_Icon")["icon"]
            if self.is_dark_mode
            else self.Icons("dark_Icon")["icon"]
        )
        # return "☀" if self.is_dark_mode else "🌙"


class ContentStyles:
    @staticmethod
    def get_Separator_style(theme_manager):
        return {
            "height": 2,
            "corner_radius": 1,
            "fg_color": theme_manager.base_bg,
        }

    @staticmethod
    def get_Action_Container_style(theme_manager):
        return {
            "height": 180 - 30,
            "corner_radius": 19,
            "fg_color": theme_manager.secondaryColor,
            "border_width": 1,
            "border_color": theme_manager.base_bg,
        }

    @staticmethod
    def get_TextBox_Container_style():
        return {
            "corner_radius": 9,
            "fg_color": "transparent",
        }

    @staticmethod
    def get_TextBox_style(theme_manager):
        return {
            "font": ("Jura", 16),
            "text_color": theme_manager.font_Secondary,
            "width": 731,
            "height": 90 - 30,
            "corner_radius": 9,
            "fg_color": theme_manager.secondaryColor,
            "scrollbar_button_color": theme_manager.base_bg,
            "wrap": "word",
        }

    @staticmethod
    def get_Action_button_style(theme_manager, text):
        return {
            "text": text,
            "font": ("Jura", 16, "bold"),
            "text_color": theme_manager.font_Secondary,
            "fg_color": theme_manager.base_bg,
            "hover_color": theme_manager.hover_bg,
            "height": 33,
            "corner_radius": 9,
            "width": 144 if text == "Select image" else 77,
        }

    @staticmethod
    def get_Status_button_style(theme_manager, name):
        return {
            "image": theme_manager.Icons(name)["icon"],
            "text": "",
            "font": ("Jura", 16, "bold"),
            "text_color": theme_manager.font_Tertiary,
            "fg_color": theme_manager.tertiaryColor_OFF,
            "hover_color": theme_manager.tertiaryColor_OFF,
            "width": 24,
            "height": 24,
            "corner_radius": 5,
        }

    @staticmethod
    def get_theme_toggle_style(theme_manager):
        return {
            "text": "",
            "image": theme_manager.get_theme_icon(),
            "text_color": theme_manager.font_Tertiary,
            "fg_color": theme_manager.active_bg,
            "hover_color": theme_manager.hover_bg,
            "width": 30,
            "height": 30,
            "corner_radius": 9,
        }

    @staticmethod
    def get_ChatLable_style(theme_manager, text):
        return {
            "text": text,
            "wraplength": 300,
            "font": ("Jura", 16),
            "justify": "left",
            "text_color": theme_manager.font_Secondary,
            "fg_color": theme_manager.secondaryColor,
            "corner_radius": 9,
            "padx": 10,
            "pady": 10,
        }

    @staticmethod
    def get_Ai_Response_style(theme_manager, text):
        return {
            "text": text,
            "wraplength": 300,
            "font": ("Jura", 16),
            "justify": "left",
            "text_color": theme_manager.font_Secondary,
            "fg_color": "transparent",
            "corner_radius": 9,
        }

    @staticmethod
    def get_Code_label_style(theme_manager, text):
        return {
            "text": text,
            "wraplength": 300,
            "font": ("Courier New", 14),
            "justify": "left",
            "text_color": theme_manager.code_font,
            "fg_color": "transparent",
            "padx": 10,
            "pady": 10,
        }

    @staticmethod
    def get_Code_container_style(theme_manager):
        return {
            "fg_color": theme_manager.code_bg,
            "corner_radius": 9,
        }

    @staticmethod
    def get_Main_Title(theme_manager, text):
        return {
            "text": text,
            "font": ("Jura", 24),
            "text_color": theme_manager.font_Main,
            "justify": "center",
        }


class LayoutSettings:
    @staticmethod
    def get_Text_layout():
        return [
            ("How can I help you today?", "Main"),
            ("Message Lamsa-Ai...", "Secondary"),
        ]

    @staticmethod
    def get_Status_layout():
        return [
            ("Globe",),
            # ("Transfer",),
        ]

    @staticmethod
    def get_Action_layout():
        return [
            ("Send",),
            ("Select image",),
        ]

    @staticmethod
    def get_window_settings():
        return {
            "title": "Lamsa-Ai",
            "geometry": "1180x720",
            "minsize": (860, 668),
            "resizable": (True, True),
            "Logo": os.path.abspath("Assets/Logo/Logo.ico"),
        }
