import customtkinter as ctk
import subprocess
import os
import json
import platform
from urllib.parse import urlparse, parse_qs

SERVERS = {
    "🇩🇪 Germany Reality": "vless://891cea51-b7f2-4bb6-b322-13acf4ad4aaf@84.201.133.58:8449?flow=xtls-rprx-vision&encryption=none&type=tcp&security=reality&fp=chrome&sni=travel.yandex.ru&pbk=eWc4OGy6tScPuAS_MCVSrFpqJRj1uC9f1gh6YLc332M&spx=/#FRKN",
    "🇫🇮 Finland Ahmad": "vless://917c427f-2c3f-4b25-abd8-314b167e27cf@taktun3.kheyrienoor.ir:80?encryption=none&type=tcp&headerType=http&path=/?V_P_N_Ahmad&security=none#FIN"
}

class ConfigManager:
    @staticmethod
    def create_json(vless_link):
        parsed = urlparse(vless_link)
        params = parse_qs(parsed.query)
        
        config = {
            "inbounds": [{"port": 10808, "listen": "127.0.0.1", "protocol": "socks", "settings": {"udp": True}}],
            "outbounds": [{
                "protocol": "vless",
                "settings": {"vnext": [{"address": parsed.hostname, "port": int(parsed.port) if parsed.port else 443, "users": [{"id": parsed.username, "encryption": "none", "flow": params.get("flow", [""])[0]}]}]},
                "streamSettings": {
                    "network": params.get("type", ["tcp"])[0],
                    "security": params.get("security", ["none"])[0],
                    "realitySettings": {
                        "serverName": params.get("sni", [""])[0],
                        "publicKey": params.get("pbk", [""])[0],
                        "fingerprint": params.get("fp", ["chrome"])[0],
                        "shortId": params.get("sid", [""])[0],
                        "spiderX": params.get("spx", [""])[0]
                    } if params.get("security", [""])[0] == "reality" else {}
                }
            }]
        }
        
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
        return config_path

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FRKN VPN")
        self.geometry("400x500")
        
        self.process = None
        
        self.lbl = ctk.CTkLabel(self, text="FRKN.VPN", font=("Impact", 40))
        self.lbl.pack(pady=20)

        self.menu = ctk.CTkOptionMenu(self, values=list(SERVERS.keys()))
        self.menu.pack(pady=20)

        self.btn = ctk.CTkButton(self, text="START VPN", command=self.toggle, fg_color="green")
        self.btn.pack(pady=20)

        self.status = ctk.CTkLabel(self, text="Status: Disconnected", text_color="gray")
        self.status.pack()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_xray_binary(self):
        system = platform.system().lower()
        arch = platform.machine().lower()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        if system == "windows":
            return os.path.join(base_dir, "xray.exe")
        elif system == "darwin":
            if "arm" in arch or "aarch64" in arch:
                path = os.path.join(base_dir, "xray-macos", "arm8", "xray")
            else:
                path = os.path.join(base_dir, "xray-macos", "64", "xray")
        elif system == "linux":
            path = os.path.join(base_dir, "xray-linux", "xray")
        else:
            return None

        if path and os.path.exists(path):
            try:
                os.chmod(path, 0o755)
            except:
                pass
            return path
        return None

    def toggle(self):
        if self.process:
            self.stop()
        else:
            self.start()

    def start(self):
        link = SERVERS[self.menu.get()]
        cfg_path = ConfigManager.create_json(link)
        xray_path = self.get_xray_binary()
        
        if not xray_path or not os.path.exists(xray_path):
            self.status.configure(text="Error: Xray binary not found!", text_color="red")
            return

        try:
            c_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            self.process = subprocess.Popen(
                [xray_path, "run", "-c", cfg_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=c_flags
            )
            self.btn.configure(text="STOP VPN", fg_color="red")
            self.status.configure(text="Status: Connected (SOCKS5 10808)", text_color="green")
        except Exception as e:
            self.status.configure(text=f"Error: {str(e)}", text_color="red")

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
        self.btn.configure(text="START VPN", fg_color="green")
        self.status.configure(text="Status: Disconnected", text_color="gray")

    def on_closing(self):
        self.stop()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()