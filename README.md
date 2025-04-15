# Lamsa-Ai 🍉

**Lamsa-Ai** is a Tkinter-based desktop application that integrates with the Gemini AI API to provide intelligent responses to user prompts. It supports both text and image inputs, offering a seamless and interactive user experience.

---

## ✨ Features

- **Dynamic Theme Switching** – Toggle between light and dark modes.
- **AI-Powered Responses** – Leverages the Gemini API for generating intelligent responses.
- **Image Support** – Upload images to enhance the AI's understanding of your prompts.
- **Connection Monitoring** – Real-time internet connection status updates.
- **Customizable UI** – Built with `customtkinter` for a modern and responsive interface.

---

## 📁 Project Structure

Lamsa-Ai<br>
├── Assets<br>
│ ├── Icons # Icons used in the application<br>
│ └── Images # Additional images like logos<br>
├── BackEnd<br>
│ └── GEMINI_BackEnd.py # Handles Gemini API integration<br>
├── Style<br>
│ └── UiConfig.py # UI styling and theme management<br>
├── Status_Checker.py # Monitors internet connectivity<br>
├── main.py # Main application entry point<br>
├── .env # Default environment variables<br>
├── .env.local # Local overrides<br>
└── README.md # Project documentation<br>

---

## 🧰 Requirements

- Python 3.9 or higher
- Required Python libraries:
  - `customtkinter`
  - `Pillow`
  - `python-dotenv`
  - `google-generativeai`

---

## ⚙️ Setup

1. **Clone the repository**
    ```bash
    git clone https://github.com/Yona2803/Lamsa_Ai.git
    cd Lamsa_Ai
    ```

2. **Install the required dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure your environment variables**

    Create a `.env` file in the root directory if it doesn’t exist, and add your API keys:
    ```
    GEMINI_API_KEY=<your-gemini-api-key>
    IMGBB_API_KEY=<your-imgbb-api-key>  # Optional
    ```

4. **Run the application**
    ```bash
    python main.py
    ```

---

## 🚀 Usage

- Launch the application.
- Enter a text prompt or upload an image (try: Alt+S to select the image and Alt+Return to send).
- Click the **"Send"** button to receive a response from Gemini AI.
- Toggle between **light** and **dark** themes using the theme switcher.

---

## 🖼️ Screenshots

### Dark Mode  
*![Lamsa_Ai-Dark](https://github.com/user-attachments/assets/547a4f54-38de-4dd7-b66b-dc94495a661f)*

### Light Mode  
*![Lamsa_Ai-Light](https://github.com/user-attachments/assets/c4625753-f2b1-4b72-9045-039f65dd7262)*

---

## 🔐 Environment Variables

| Variable          | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `GEMINI_API_KEY`  | Your Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `IMGBB_API_KEY`   | *(Optional)* API key from [imgbb.com](https://imgbb.com)               |

---

## 🤝 Contributing

Contributions are welcome!  
Here’s how to get started:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add your message"`
4. Push to your branch: `git push origin feature/your-feature-name`
5. Open a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙌 Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) – for the modern UI components  
- [Pillow](https://python-pillow.org) – for image processing  
- [Google Generative AI](https://ai.google.dev/) – for the AI backend  

---

# From the river to the sea, Palestine will be free✌️ #FreePalestine 🍉🇵🇸 
