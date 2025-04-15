import os
import time
import tkinter as tk
import customtkinter as ctk
from PIL import ImageColor, Image, ImageDraw, ImageTk
from Status_Checker import ConnectionMonitor
from Style.UiConfig import ThemeManager, ContentStyles, LayoutSettings
from BackEnd.GEMINI_BackEnd import generateGeminiResponse
import ctypes

textPrompt = None
imgFile = None

# Create connection monitor instance
connection_monitor = ConnectionMonitor(check_interval=1)  # Check every 1 second


def normalize_color(color):
    try:
        rgb = ImageColor.getrgb(str(color))
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    except:
        return str(color).lower()


class LamsaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.theme_manager = ThemeManager(is_dark_mode=False)
        self.old_colors = {}
        self.save_current_colors()

        window_settings = LayoutSettings.get_window_settings()
        self.title(window_settings["title"])
        self.geometry(window_settings["geometry"])
        self.minsize(*window_settings["minsize"])
        self.resizable(*window_settings["resizable"])
        self.iconbitmap(window_settings["Logo"])

        ctk.set_appearance_mode(self.theme_manager.get_theme_mode())
        ctk.set_default_color_theme("blue")

        self.option_buttons = []
        self.widget_refs = []
        self.connection_button = (
            None  # Will store reference to connection status button
        )
        self.SelectFile_button = None  # Will store reference to Select image button
        self.create_widgets()

        self.animation_steps = 15
        self.animation_delay = 12
        self.transitioning = False

        # Message animation parameters
        self.message_animation_steps = 10
        self.message_animation_delay = 10

        # Start the connection monitor
        connection_monitor.start()

        # Update connection status periodically
        self.update_connection_status()

    def save_current_colors(self):
        self.old_colors = {
            key: normalize_color(value)
            for key, value in {
                "primaryColor": self.theme_manager.primaryColor,
                "secondaryColor": self.theme_manager.secondaryColor,
                "tertiaryColor_ON": self.theme_manager.tertiaryColor_ON,
                "tertiaryColor_OFF": self.theme_manager.tertiaryColor_OFF,
                "font_Main": self.theme_manager.font_Main,
                "font_Secondary": self.theme_manager.font_Secondary,
                "font_Tertiary": self.theme_manager.font_Tertiary,
                "base_bg": self.theme_manager.base_bg,
                "hover_bg": self.theme_manager.hover_bg,
                "active_bg": self.theme_manager.active_bg,
                "code_bg": self.theme_manager.code_bg,
                "code_font": self.theme_manager.code_font,
            }.items()
        }

    def create_widgets(self):
        self.configure(fg_color=self.theme_manager.primaryColor)

        container_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        container_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        theme_toggle_frame = ctk.CTkFrame(
            container_frame, fg_color="transparent", width=35
        )
        theme_toggle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        theme_toggle_frame.pack_propagate(False)

        theme_toggle_style = ContentStyles.get_theme_toggle_style(self.theme_manager)
        self.theme_toggle = ctk.CTkButton(
            theme_toggle_frame, **theme_toggle_style, command=self.switch_theme
        )
        self.theme_toggle.pack(anchor="n", pady=0)

        main_frame = ctk.CTkFrame(
            container_frame, width=755, fg_color="transparent", corner_radius=0
        )
        main_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        main_frame.pack_propagate(False)

        chat_frame = ctk.CTkFrame(
            main_frame, fg_color="transparent", border_width=0, corner_radius=19
        )
        chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.widget_refs.append((chat_frame, "transparent"))

        # Create a frame for initial appearance
        self.initial_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        self.initial_frame.pack(expand=True)  # This will center the frame

        img = ctk.CTkImage(
            light_image=Image.open("Assets/Icons/Bot.png"), size=(186, 186)
        )
        img_label = ctk.CTkLabel(self.initial_frame, image=img, text="")
        img_label.pack(pady=(0))

        text = LayoutSettings.get_Text_layout()[0]
        title_label = ctk.CTkLabel(
            self.initial_frame,
            **ContentStyles.get_Main_Title(self.theme_manager, text[0]),
        )
        title_label.pack(pady=(9, 0))
        self.widget_refs.append((title_label, "font_Main"))

        # Add scrollable chat area (initially hidden)
        self.chat_scroll = ctk.CTkScrollableFrame(
            chat_frame, fg_color="transparent", corner_radius=9
        )
        # Don't pack it initially - we'll show it when first message is sent
        # Add chat scroll frame to widget_refs
        self.widget_refs.append((self.chat_scroll, "chat_frame"))

        Action_frame = ctk.CTkFrame(
            main_frame, **ContentStyles.get_Action_Container_style(self.theme_manager)
        )
        Action_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 22))
        # Action_frame.pack_propagate(False)
        self.widget_refs.append((Action_frame, "action_container"))

        textbox_container = ctk.CTkFrame(
            Action_frame,
            **ContentStyles.get_TextBox_Container_style(),
        )
        textbox_container.pack(fill=tk.X, padx=12, pady=(10, 0))

        # Create attachment preview frame (initially hidden)
        self.attachment_preview = ctk.CTkFrame(
            textbox_container,
            fg_color=self.theme_manager.base_bg,
            height=30,
            corner_radius=9,
        )
        # Don't pack yet - we'll show it when an image is selected
        # Add attachment preview to widget_refs if it exists
        if hasattr(self, "attachment_preview"):
            self.widget_refs.append((self.attachment_preview, "attachment_preview"))

        text, text_type = LayoutSettings.get_Text_layout()[1]
        placeholder_text = text

        def on_textbox_focus_in(event):
            if self.textbox.get("1.0", "end-1c") == placeholder_text:
                self.textbox.delete("1.0", "end")

        def on_textbox_focus_out(event):
            if self.textbox.get("1.0", "end-1c") == "":
                self.textbox.insert("1.0", placeholder_text)

        def on_key_press(event):
            if (
                event.keysym == "Return"
                and (event.state & 0x00020000)  # Check for Alt key
                and not event.state & 1  # Check if Shift is not pressed
            ):
                self.sendRequest()
                return "break"

            if (
                event.char.lower() == "s"
                and (event.state & 0x00020000)  # Check for Alt key
                and not event.state & 1  # Check if Shift is not pressed
            ):
                self.select_file()
                return "break"

        self.textbox = ctk.CTkTextbox(
            textbox_container,
            **ContentStyles.get_TextBox_style(self.theme_manager),
        )
        self.textbox.insert("1.0", placeholder_text)
        self.textbox.bind("<FocusIn>", on_textbox_focus_in)
        self.textbox.bind("<FocusOut>", on_textbox_focus_out)
        self.textbox.bind("<KeyRelease>", self.on_text_change)
        self.bind("<KeyPress>", on_key_press)

        self.textbox.pack(pady=(0, 5))
        # Add textbox to widget_refs for theme transitions
        self.widget_refs.append((self.textbox, "textbox"))

        separator = ctk.CTkFrame(
            Action_frame, **ContentStyles.get_Separator_style(self.theme_manager)
        )
        separator.pack(fill=tk.X, padx=14, pady=(5))
        self.widget_refs.append((separator, "base_bg"))

        bottom_btns_frame = ctk.CTkFrame(
            Action_frame, fg_color="transparent", height=33
        )
        bottom_btns_frame.pack(fill=tk.X, padx=12, pady=(4, 11))
        bottom_btns_frame.pack_propagate(False)

        def Icons(name):
            path = f"Assets/Icons/{name}.png"
            if os.path.exists(path):
                return {"icon": ctk.CTkImage(Image.open(path), size=(21, 21))}
            return {"icon": None}  # Return dict with None icon if file doesn't exist

        for text in LayoutSettings.get_Action_layout():
            btn = ctk.CTkButton(
                bottom_btns_frame,
                # **({'image': Icons("Disable")["icon"]} if text[0] != "Select image" else {}),
                **ContentStyles.get_Action_button_style(self.theme_manager, text[0]),
                command=(
                    self.select_file if text[0] == "Select image" else self.sendRequest
                ),
            )
            btn.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
            self.widget_refs.append((btn, "action_button"))

            if (
                text[0] == "Select image"
            ):  # The first button is responsible for selecting Images
                self.SelectFile_button = btn
            else:
                self.Send_button = btn

        status_frame = ctk.CTkFrame(container_frame, width=30, fg_color="transparent")
        status_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        status_frame.pack_propagate(False)

        # Status layout buttons with specific handling for connection button
        status_layout = LayoutSettings.get_Status_layout()
        for i, name in enumerate(status_layout):
            btn = ctk.CTkButton(
                status_frame,
                **ContentStyles.get_Status_button_style(self.theme_manager, name[0]),
            )
            btn.pack(anchor="n", padx=0, pady=4)
            self.widget_refs.append((btn, "status_button"))

            # Save reference to the first button (Globe/Connection)
            if i == 0:  # The first button in the status layout
                self.connection_button = btn

    def on_text_change(self, event=None):
        content = self.textbox.get("1.0", "end-1c")  # .strip()

        if content == "":
            self.Send_button.configure(
                fg_color=self.theme_manager.base_bg,
                text_color=self.theme_manager.font_Secondary,
            )
        else:
            self.Send_button.configure(
                fg_color=self.theme_manager.active_bg,
                text_color=self.theme_manager.font_Tertiary,
            )

    def select_file(self):
        filetypes = (("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*"))

        img_path = ctk.filedialog.askopenfilename(
            title="Select an image file", filetypes=filetypes
        )

        if img_path:
            if self.SelectFile_button:
                self.SelectFile_button.configure(
                    fg_color=self.theme_manager.active_bg,
                    text_color=self.theme_manager.font_Tertiary,
                )
            global imgFile
            imgFile = img_path

            # Display image preview in attachment area
            self.show_attachment_preview(img_path)

            return img_path
        return None

    def show_attachment_preview(self, img_path):
        # Clear any existing previews
        if (
            hasattr(self, "attachment_preview")
            and self.attachment_preview.winfo_exists()
        ):
            for widget in self.attachment_preview.winfo_children():
                widget.destroy()

        # If we have no attachment preview frame yet, create it
        if not self.attachment_preview.winfo_ismapped():
            self.attachment_preview.pack(
                fill=tk.X, padx=0, pady=(0, 5), before=self.textbox
            )

        try:
            # Create a thumbnail for the preview
            img = Image.open(img_path)
            img.thumbnail((30, 30))

            # Store the thumbnail to prevent garbage collection
            self.thumbnail_image = ImageTk.PhotoImage(img)

            # Get filename for display
            filename = os.path.basename(img_path)
            if len(filename) > 20:
                filename = filename[:17] + "..."

            # Create preview layout
            preview_label = ctk.CTkLabel(
                self.attachment_preview,
                text=filename,
                image=self.thumbnail_image,
                compound="left",
                padx=5,
                pady=2,
                font=("Segoe UI", 10),
            )
            preview_label.pack(side=tk.LEFT, padx=5)

            # Add remove button
            remove_btn = ctk.CTkButton(
                self.attachment_preview,
                text="✕",
                width=20,
                height=20,
                fg_color="transparent",
                hover_color=self.theme_manager.hover_bg,
                text_color=self.theme_manager.font_Secondary,
                command=self.remove_attachment,
            )
            remove_btn.pack(side=tk.RIGHT, padx=5)

        except Exception as e:
            print(f"Error creating preview: {e}")

    def remove_attachment(self):
        global imgFile
        imgFile = None

        # Reset button state
        if self.SelectFile_button:
            self.SelectFile_button.configure(
                fg_color=self.theme_manager.base_bg,
                text_color=self.theme_manager.font_Secondary,
            )

        # Hide preview
        if (
            hasattr(self, "attachment_preview")
            and self.attachment_preview.winfo_ismapped()
        ):
            self.attachment_preview.pack_forget()

    def display_user_message(self, message, imgFile):
        """Display a message from the user in the chat frame with styled label and optional image."""
        # Main container for the whole message (text + optional image) set to fixed width (348px)
        message_container = ctk.CTkFrame(
            self.chat_scroll,
            width=348,
            fg_color="transparent",
        )
        message_container.message_source = "user"
        message_container.pack(fill=tk.X, padx=0, pady=(10, 15), anchor=tk.E)

        # --- Optional image container ---
        if imgFile:
            try:
                # Load and resize image maintaining aspect ratio
                img = Image.open(imgFile)
                original_width, original_height = img.size
                max_width = 348
                scale = max_width / original_width
                new_height = int(original_height * scale)

                # Resize image first
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                # Apply rounded corners (with a radius of 9 pixels)
                # Ensure image has an alpha channel
                img = img.convert("RGBA")
                w, h = img.size

                # Create a mask
                mask = Image.new("L", (w, h), 0)
                draw = ImageDraw.Draw(mask)
                # Draw a rounded rectangle on the mask (filled white)
                draw.rounded_rectangle((0, 0, w, h), radius=9, fill=255)

                # Apply the mask to the image
                img.putalpha(mask)

                # Create a CTkImage from the processed image
                ctk_img = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(max_width, new_height),
                )

                img_label = ctk.CTkLabel(
                    message_container,
                    text="",
                    image=ctk_img,
                    compound="top",
                    justify="right",
                    fg_color="transparent",
                    corner_radius=9,
                    padx=0,
                    pady=10,
                )
                img_label.pack(fill=tk.Y, anchor=tk.E, padx=0, pady=10)

            except Exception as e:
                print(f"Error loading image: {e}")

        message_label = ctk.CTkLabel(
            message_container,
            **ContentStyles.get_ChatLable_style(self.theme_manager, message),
        )
        message_label.pack(fill=tk.Y, anchor=tk.E, padx=0, pady=0)

        # Animate the message appearance
        self.animate_message_appearance(message_container)
        # Scroll to bottom
        self.after(50, self.scroll_to_bottom)

    def display_ai_response(self, message):
        """Display a response from the AI in the chat frame with improved layout"""
        # Clean extra newlines before processing
        message = message.strip()  # Remove leading/trailing whitespace
        message = "\n".join(
            line for line in message.splitlines() if line.strip()
        )  # Remove empty lines

        # Create a single message frame for all content
        message_frame = ctk.CTkFrame(
            self.chat_scroll,
            width=348,
            fg_color="transparent",
        )
        message_frame.message_source = "ai"
        message_frame.pack(fill=tk.Y, padx=0, pady=(10, 15), anchor=tk.W)

        # Create an inner frame to contain all message components (aligned left)
        content_frame = ctk.CTkFrame(
            message_frame,
            fg_color="transparent",
            width=328,
        )
        content_frame.pack(side=tk.LEFT, padx=10)

        # Render the message content within the content frame
        self.render_gemini_message(content_frame, message)

        # Add copy icon under the response
        self.add_copy_icon(message_frame, message)

        # Animate the message appearance
        self.animate_message_appearance(message_frame)

        # Scroll to bottom after a short delay
        self.after(50, self.scroll_to_bottom)

    def render_gemini_message(self, parent_frame, message):
        """Render message content with proper formatting for code blocks and text"""
        import re

        lines = message.splitlines()
        in_code_block = False
        code_lines = []
        current_text_block = []

        def render_text_block():
            if current_text_block:
                text_content = "\n".join(current_text_block)
                text_label = ctk.CTkLabel(
                    parent_frame,
                    **ContentStyles.get_Ai_Response_style(
                        self.theme_manager, text_content
                    ),
                )
                text_label.pack(fill=tk.X, padx=0, pady=(0, 5), anchor=tk.W)
                current_text_block.clear()

        for line in lines:
            # Handle code block delimiters
            if line.strip().startswith("```"):
                # If we have text content pending, render it before the code block
                render_text_block()

                in_code_block = not in_code_block

                # When exiting a code block, render it
                # if not in_code_block and code_lines:
                #     code_text = "\n".join(code_lines)
                #     code_frame = ctk.CTkFrame(
                #         parent_frame,
                #         **ContentStyles.get_Code_container_style(self.theme_manager),
                #     )
                #     code_frame.pack(fill=tk.X, padx=0, pady=(0, 5), anchor=tk.W)

                #     code_label = ctk.CTkLabel(
                #         code_frame,
                #         **ContentStyles.get_Code_label_style(
                #             self.theme_manager, code_text
                #         ),
                #     )
                #     code_label.pack(fill=tk.X, padx=0, pady=0)
                #     code_lines.clear()
                # When exiting a code block, render it
                if not in_code_block and code_lines:
                    code_text = "\n".join(code_lines)
                    code_frame = ctk.CTkFrame(
                        parent_frame,
                        **ContentStyles.get_Code_container_style(self.theme_manager),
                    )
                    # Add attribute to identify this as a code container
                    code_frame.is_code_container = True
                    code_frame.pack(fill=tk.X, padx=0, pady=(0, 5), anchor=tk.W)

                    code_label = ctk.CTkLabel(
                        code_frame,
                        **ContentStyles.get_Code_label_style(
                            self.theme_manager, code_text
                        ),
                    )
                    # Add attribute to identify this as a code label
                    code_label.is_code_label = True
                    code_label.pack(fill=tk.X, padx=0, pady=0)
                    code_lines.clear()

                continue

            # Collect code lines or text lines
            if in_code_block:
                code_lines.append(line)
            else:
                # Handle basic markdown-like formatting
                if line.strip().startswith("- "):
                    line = "• " + line.strip()[2:]

                # Clean up markdown formatting (just remove for now)
                clean_line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
                current_text_block.append(clean_line)

        # Handle any remaining text after processing all lines
        render_text_block()

        # Handle any unfinished code block (in case message ended without closing ```)
        if code_lines:
            code_text = "\n".join(code_lines)
            code_frame = ctk.CTkFrame(
                parent_frame,
                **ContentStyles.get_Code_container_style(self.theme_manager),
            )
            code_frame.pack(fill=tk.X, padx=0, pady=(0, 5), anchor=tk.W)

            code_label = ctk.CTkLabel(
                code_frame,
                **ContentStyles.get_Code_label_style(self.theme_manager, code_text),
            )
            code_label.pack(fill=tk.X, padx=0, pady=0)

    def add_copy_icon(self, parent_frame, message):
        """Add a small copy text icon under the response frame"""

        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(message)
            self.update()

            # Optional: Show feedback tooltip or briefly change icon to indicate copying
            original_text = copy_icon.cget("text")
            original_color = copy_icon.cget("text_color")

            copy_icon.configure(text="✔", text_color=self.theme_manager.active_bg)
            parent_frame.after(
                1500,
                lambda: copy_icon.configure(
                    text=original_text, text_color=original_color
                ),
            )

        # Create a frame at the bottom to hold the copy icon
        icon_frame = ctk.CTkFrame(
            parent_frame,
            fg_color="transparent",
        )
        icon_frame.pack(fill=tk.Y, anchor=tk.S, side=tk.BOTTOM, padx=0, pady=(3, 0))

        # Create the copy icon label with hover effect
        copy_icon = ctk.CTkLabel(
            icon_frame,
            text="📋",
            font=("Segoe UI Emoji", 16),  # Using a font that supports emoji
            text_color=(self.theme_manager.font_Secondary),
            fg_color="transparent",
            cursor="hand2",  # Change cursor to hand when hovering
        )
        copy_icon.pack(side=tk.BOTTOM, padx=(0, 10))

        # Bind click event
        copy_icon.bind("<Button-1>", lambda e: copy_to_clipboard())

        # Optional: Add hover effect
        def on_enter(e):
            copy_icon.configure(text_color=(self.theme_manager.font_Main))

        def on_leave(e):
            copy_icon.configure(text_color=(self.theme_manager.font_Secondary))

        copy_icon.bind("<Enter>", on_enter)
        copy_icon.bind("<Leave>", on_leave)

    def display_system_message(self, message):
        """Display a system message in the chat frame"""
        message_frame = ctk.CTkFrame(
            self.chat_scroll,
            width=348,
            fg_color="transparent",
        )
        message_frame.pack(fill=tk.X, padx=0, pady=(10, 15), anchor=tk.W)

        # Message content
        message_label = ctk.CTkLabel(
            message_frame,
            **ContentStyles.get_Ai_Response_style(self.theme_manager, message),
        )
        message_label.pack(
            side=tk.BOTTOM,
            fill=tk.Y,
            anchor=tk.W,
            padx=0,
            pady=0,
        )

        # Scroll to bottom
        self.chat_scroll.update()
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

        # Return the frame so we can remove it later
        return message_frame

    def animate_message_appearance(self, widget, opacity=0):
        """Animate the appearance of a message by fading it in"""
        if opacity <= 1.0:
            # Set the widget's opacity
            widget.configure(
                fg_color=self.adjust_color_opacity(widget.cget("fg_color"), opacity)
            )
            # Schedule the next animation step
            self.after(
                self.message_animation_delay,
                lambda: self.animate_message_appearance(widget, opacity + 0.1),
            )

    def adjust_color_opacity(self, color, opacity):
        """Adjust a color's opacity (for animation effects)"""
        if color == "transparent":
            return color

        try:
            rgb = ImageColor.getrgb(color)
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}{int(opacity * 255):02x}"
        except:
            return color

    def start_conversation(self):
        """Switch from initial screen to chat interface"""
        if hasattr(self, "initial_frame") and self.initial_frame.winfo_exists():
            self.initial_frame.pack_forget()  # Hide initial screen

        # Show the chat interface if not already showing
        if hasattr(self, "chat_scroll") and not self.chat_scroll.winfo_ismapped():
            self.chat_scroll.pack(fill=tk.BOTH, expand=True, padx=0, pady=10)

    def scroll_to_bottom(self):
        """Ensure the chat view scrolls to the most recent message"""
        if hasattr(self, "chat_scroll") and self.chat_scroll.winfo_exists():
            self.chat_scroll.update()
            self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def sendRequest(self):
        # Get current connection status from the monitor
        is_connected = connection_monitor.is_connected
        if not is_connected:

            def Mbox(title, text, style):
                return ctypes.windll.user32.MessageBoxW(0, text, title, style)

            Mbox(
                "Internet Issue",
                "No internet connection. Please check your connection.",
                0,
            )
            return

        global imgFile, textPrompt
        textPrompt = self.textbox.get("1.0", "end-1c")

        # Clean extra newlines before processing
        textPrompt = textPrompt.strip()  # Remove leading/trailing whitespace
        textPrompt = "\n".join(
            line for line in textPrompt.splitlines() if line.strip()
        )  # Remove empty lines

        if not textPrompt or textPrompt == "":
            return  # No text entered

        # Check if the text is the placeholder or empty
        placeholder_text = LayoutSettings.get_Text_layout()[1][0]
        if textPrompt == placeholder_text or not textPrompt.strip():
            return

        # Switch to conversation mode
        self.start_conversation()

        # Display user message in chat
        self.display_user_message(textPrompt, imgFile)

        # Clear the textbox
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", "")  # Keep it empty after sending

        # Remove image preview if exists
        if imgFile:
            # Reset button state
            if self.SelectFile_button:
                self.SelectFile_button.configure(
                    fg_color=self.theme_manager.base_bg,
                    text_color=self.theme_manager.font_Secondary,
                )

            # Hide preview
            if (
                hasattr(self, "attachment_preview")
                and self.attachment_preview.winfo_ismapped()
            ):
                self.attachment_preview.pack_forget()

        self.Send_button.configure(
            fg_color=self.theme_manager.base_bg,
            text_color=self.theme_manager.font_Secondary,
        )

        # Show processing message
        processing_msg = "Waiting for response..."
        waiting_frame = self.display_system_message(processing_msg)

        # Force update to show the waiting message
        self.update_idletasks()

        # Ensure at least 1 second of waiting time
        start_time = time.time()

        try:
            # Call Gemini API
            geminiResponse = generateGeminiResponse(imgFile, textPrompt)

            # Ensure minimum wait time of 1 second
            elapsed = time.time() - start_time
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)

            # Remove the waiting message
            if waiting_frame and waiting_frame.winfo_exists():
                waiting_frame.destroy()

            if geminiResponse:
                # Display the AI response in chat
                self.display_ai_response(geminiResponse)
            else:
                self.display_system_message("No response received from Gemini API.")

            imgFile = None  # Reset image file after processing
            textPrompt = None  # Reset text prompt after processing

        except Exception as e:
            # Remove the waiting message
            if waiting_frame and waiting_frame.winfo_exists():
                waiting_frame.destroy()

            error_message = f"Error: {str(e)}"
            self.display_system_message(error_message)
            import traceback

            traceback.print_exc()

    def update_connection_status(self):
        """Update the connection status button based on internet connectivity"""
        if self.connection_button:
            # Get current connection status from the monitor
            is_connected = connection_monitor.is_connected

            if is_connected:
                # Connected - use ON color
                new_color = self.theme_manager.tertiaryColor_ON
            else:
                # Disconnected - use OFF color
                new_color = self.theme_manager.tertiaryColor_OFF

            # Update the button colors
            self.connection_button.configure(
                fg_color=new_color, hover_color=new_color  # Same color for hover state
            )

        # Schedule the next update (every 1000ms = 1 second)
        self.after(1000, self.update_connection_status)

    def select_option_button(self, selected_text):
        global textPrompt
        textPrompt = selected_text

        for btn in self.option_buttons:
            # Compare button text with the selected value
            if btn.cget("text") == selected_text:
                btn.configure(
                    fg_color=self.theme_manager.active_bg,
                    text_color=self.theme_manager.font_Tertiary,
                )
            else:
                btn.configure(
                    fg_color=self.theme_manager.base_bg,
                    text_color=self.theme_manager.font_Secondary,
                )

    def switch_theme(self):
        if self.transitioning:
            return

        # Save focus state
        focused_widget = self.focus_get()

        self.transitioning = True
        self.save_current_colors()
        self.theme_manager.toggle_theme()
        ctk.set_appearance_mode(self.theme_manager.get_theme_mode())

        self.theme_toggle.configure(image=self.theme_manager.get_theme_icon())
        self.animate_color_transition(0)
        self.after(
            self.animation_steps * self.animation_delay + 150,
            lambda: [
                self.update_all_widget_colors(),
                setattr(self, "transitioning", False),
                # Restore focus if widget still exists
                (
                    focused_widget.focus_set()
                    if focused_widget and focused_widget.winfo_exists()
                    else None
                ),
            ],
        )

    def animate_color_transition(self, step):
        if step <= self.animation_steps:
            factor = step / self.animation_steps
            self.update_colors_with_transition(factor)
            self.update_chat_messages(factor)
            self.after(
                self.animation_delay, lambda: self.animate_color_transition(step + 1)
            )

    def update_all_widget_colors(self):
        self.configure(fg_color=self.theme_manager.primaryColor)
        for widget, role in self.widget_refs:
            self.update_widget_color(widget, role, 1.0)

        # Update connection status after theme change
        self.update_connection_status()

        # Ensure all chat messages, including those inside code containers,
        # are updated to use the new theme.
        self.update_chat_messages(1.0)

    def update_colors_with_transition(self, factor):
        transition_primary = self.interpolate_color(
            self.old_colors["primaryColor"],
            normalize_color(self.theme_manager.primaryColor),
            factor,
        )
        self.configure(fg_color=transition_primary)
        for widget, role in self.widget_refs:
            self.update_widget_color(widget, role, factor)

    def update_widget_color(self, widget, role, factor):
        role_map = {
            "primaryColor": normalize_color(self.theme_manager.primaryColor),
            "secondaryColor": normalize_color(self.theme_manager.secondaryColor),
            "tertiaryColor_ON": normalize_color(self.theme_manager.tertiaryColor_ON),
            "tertiaryColor_OFF": normalize_color(self.theme_manager.tertiaryColor_OFF),
            "font_Main": normalize_color(self.theme_manager.font_Main),
            "font_Secondary": normalize_color(self.theme_manager.font_Secondary),
            "font_Tertiary": normalize_color(self.theme_manager.font_Tertiary),
            "base_bg": normalize_color(self.theme_manager.base_bg),
            "hover_bg": normalize_color(self.theme_manager.hover_bg),
            "active_bg": normalize_color(self.theme_manager.active_bg),
            "code_bg": normalize_color(self.theme_manager.code_bg),
            "code_font": normalize_color(self.theme_manager.code_font),
        }

        if role in ("font_Main", "font_Secondary", "font_Tertiary"):
            old = self.old_colors[role]
            new = role_map[role]
            widget.configure(text_color=self.interpolate_color(old, new, factor))

        elif role == "base_bg" or role == "secondaryColor":
            old = self.old_colors[role]
            new = role_map[role]
            widget.configure(fg_color=self.interpolate_color(old, new, factor))

        elif role == "action_container":
            old_fg = self.old_colors["secondaryColor"]
            new_fg = role_map["secondaryColor"]
            old_border = self.old_colors["base_bg"]
            new_border = role_map["base_bg"]
            widget.configure(
                fg_color=self.interpolate_color(old_fg, new_fg, factor),
                border_color=self.interpolate_color(old_border, new_border, factor),
            )

        # Separate handling for option buttons: maintain active colors if selected
        elif role == "option_button":
            if widget.cget("text") == textPrompt:
                old_fg = self.old_colors["active_bg"]
                new_fg = role_map["active_bg"]
                old_hover = self.old_colors["hover_bg"]
                new_hover = role_map["hover_bg"]
                old_text = self.old_colors["font_Tertiary"]
                new_text = role_map["font_Tertiary"]
                widget.configure(
                    fg_color=self.interpolate_color(old_fg, new_fg, factor),
                    hover_color=self.interpolate_color(old_hover, new_hover, factor),
                    text_color=self.interpolate_color(old_text, new_text, factor),
                )
            else:
                old_fg = self.old_colors["base_bg"]
                new_fg = role_map["base_bg"]
                old_hover = self.old_colors["hover_bg"]
                new_hover = role_map["hover_bg"]
                old_text = self.old_colors["font_Secondary"]
                new_text = role_map["font_Secondary"]
                widget.configure(
                    fg_color=self.interpolate_color(old_fg, new_fg, factor),
                    hover_color=self.interpolate_color(old_hover, new_hover, factor),
                    text_color=self.interpolate_color(old_text, new_text, factor),
                )

        elif role == "action_button":
            # Skip updating the SelectFile_button so its colors remain unchanged
            if widget == self.SelectFile_button and imgFile:
                return

            old_fg = self.old_colors["base_bg"]
            new_fg = role_map["base_bg"]
            old_hover = self.old_colors["hover_bg"]
            new_hover = role_map["hover_bg"]
            old_text = self.old_colors["font_Secondary"]
            new_text = role_map["font_Secondary"]
            widget.configure(
                fg_color=self.interpolate_color(old_fg, new_fg, factor),
                hover_color=self.interpolate_color(old_hover, new_hover, factor),
                text_color=self.interpolate_color(old_text, new_text, factor),
            )

        elif role == "status_button":
            # Skip connection button during theme transition as it will be updated separately
            if widget == self.connection_button:
                return

            old = self.old_colors["tertiaryColor_OFF"]
            new = role_map["tertiaryColor_OFF"]
            color = self.interpolate_color(old, new, factor)
            widget.configure(fg_color=color, hover_color=color)

        elif role == "textbox":
            old_fg = self.old_colors["base_bg"]
            new_fg = role_map["base_bg"]
            old_text = self.old_colors["font_Secondary"]
            new_text = role_map["font_Secondary"]
            old_border = self.old_colors["hover_bg"]
            new_border = role_map["hover_bg"]

            widget.configure(
                fg_color=self.interpolate_color(old_fg, new_fg, factor),
                text_color=self.interpolate_color(old_text, new_text, factor),
                border_color=self.interpolate_color(old_border, new_border, factor),
            )

        # Add handling for chat frame
        elif role == "chat_frame":
            old_fg = self.old_colors["primaryColor"]
            new_fg = role_map["primaryColor"]
            widget.configure(fg_color=self.interpolate_color(old_fg, new_fg, factor))

        # Add handling for attachment preview
        elif role == "attachment_preview":
            old_fg = self.old_colors["base_bg"]
            new_fg = role_map["base_bg"]
            old_border = self.old_colors["hover_bg"]
            new_border = role_map["hover_bg"]

            widget.configure(
                fg_color=self.interpolate_color(old_fg, new_fg, factor),
                border_color=self.interpolate_color(old_border, new_border, factor),
            )

        # Add handling for code container/ label
        elif role == "code_container":
            old_bg = self.old_colors["code_bg"]
            new_bg = role_map["code_bg"]
            widget.configure(fg_color=self.interpolate_color(old_bg, new_bg, factor))

        elif role == "code_label":
            old_text = self.old_colors["code_font"]
            new_text = role_map["code_font"]
            widget.configure(
                text_color=self.interpolate_color(old_text, new_text, factor)
            )

    def update_chat_messages(self, factor):
        if hasattr(self, "chat_scroll") and self.chat_scroll.winfo_exists():
            for message_container in self.chat_scroll.winfo_children():
                if isinstance(message_container, ctk.CTkFrame):
                    # Determine message source
                    message_source = getattr(
                        message_container, "message_source", "unknown"
                    )

                    # Process based on source
                    self.process_message_frame(
                        message_container, factor, message_source
                    )

    def process_message_frame(self, frame, factor, message_source):
        # If the frame is a code container, update its own background
        if hasattr(frame, "is_code_container") and frame.is_code_container:
            old_bg = self.old_colors["code_bg"]
            new_bg = normalize_color(self.theme_manager.code_bg)
            frame.configure(fg_color=self.interpolate_color(old_bg, new_bg, factor))

        # Always process children, regardless of the frame type
        for child in frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                self.process_message_frame(child, factor, message_source)
            elif isinstance(child, ctk.CTkLabel):
                if hasattr(child, "is_code_label") and child.is_code_label:
                    # Update code label text color
                    old_text = self.old_colors["code_font"]
                    new_text = normalize_color(self.theme_manager.code_font)
                    child.configure(
                        text_color=self.interpolate_color(old_text, new_text, factor)
                    )
                else:
                    # Regular label update based on message source
                    old_text = self.old_colors["font_Secondary"]
                    new_text = normalize_color(self.theme_manager.font_Secondary)
                    if message_source == "user":
                        old_bg = self.old_colors["secondaryColor"]
                        new_bg = normalize_color(self.theme_manager.secondaryColor)
                    else:
                        old_bg = self.old_colors["primaryColor"]
                        new_bg = normalize_color(self.theme_manager.primaryColor)
                    child.configure(
                        fg_color=self.interpolate_color(old_bg, new_bg, factor),
                        text_color=self.interpolate_color(old_text, new_text, factor),
                    )

    def interpolate_color(self, old_color, new_color, factor):
        if old_color in (None, "transparent") or new_color in (None, "transparent"):
            return new_color
        try:
            old_rgb = ImageColor.getrgb(old_color)
            new_rgb = ImageColor.getrgb(new_color)
            blended_rgb = tuple(
                int(old_rgb[i] + (new_rgb[i] - old_rgb[i]) * factor) for i in range(3)
            )
            return f"#{blended_rgb[0]:02x}{blended_rgb[1]:02x}{blended_rgb[2]:02x}"
        except:
            return new_color

    def on_closing(self):
        """Clean up resources when closing the application"""
        # Stop the connection monitor
        connection_monitor.stop()
        # Destroy the window
        self.destroy()


if __name__ == "__main__":
    app = LamsaApp()
    # Set up proper cleanup when closing the window
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
