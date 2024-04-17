import tkinter as tk
from datetime import datetime
import psutil
import requests
from PIL import Image, ImageTk
import os
from dotenv import load_dotenv

class TinyTaskbar(tk.Tk):
    def __init__(self):
        super().__init__()
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        self.title("TinyTaskbar")
        self.geometry("300x100")
        self.overrideredirect(True)
        self.trasp = "gray1"
        self.opacity = 1.0
        self.show_battery = True
        self.locked = False
        self.wm_attributes("-topmost", True)
        self.wm_attributes("-transparentcolor", self.trasp)
        self.configure(bg=self.trasp)

        self.time_label = tk.Label(self, fg='white', font=('Ubuntu', 14, 'bold'), bg=self.trasp, bd=0, anchor="w", justify="left")
        self.time_label.place(relx=0.32, rely=0.415)

        self.battery_icon = Image.open("assets/battery_icon.png").resize((50, 50))
        self.battery_icon = ImageTk.PhotoImage(self.battery_icon)
        self.battery_label = tk.Label(self, image=self.battery_icon, bg=self.trasp)
        self.battery_label.place(relx=0.1, rely=0.4)

        self.battery_percent = tk.Label(self, fg='white', font=('Ubuntu', 8, 'bold'), bg=self.trasp, bd=0)
        self.battery_percent.place(relx=0.13, rely=0.6)

        self.weather_label = tk.Label(self, fg='white', font=('Ubuntu', 10, 'bold'), bg=self.trasp, bd=0)
        self.weather_label.place(relx=0.81, rely=0.46)
        self.weather_temperature = tk.Label(self, fg='white', font=('Ubuntu', 10, 'bold'), bg=self.trasp, bd=0)
        self.weather_temperature.place(relx=0.71, rely=0.53)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Lock", command=self.lock)
        self.context_menu.add_command(label="Change City", command=self.change_city)
        self.context_menu.add_command(label="Change Opacity", command=self.change_opacity)
        self.context_menu.add_command(label="Display Battery", command=self.toggle_battery)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Quit", command=self.close_window)

        self.bind("<Button-3>", self.show_context_menu)

        self.start_x = 0
        self.start_y = 0

        self.bind("<Button-1>", self.on_drag_start)
        self.bind("<B1-Motion>", self.on_drag_motion)
        self.bind("<ButtonRelease-1>", self.on_drag_release)

        self.update_time()
        self.update_battery()
        self.update_weather()

    def update_time(self):
        current_time = datetime.now().strftime("%Hh%M")
        current_date = datetime.now().strftime("%d/%m/%Y")
        self.time_label.config(text=current_time + '\n' + current_date)
        self.after(1000, self.update_time)

    def update_battery(self):
        if not self.show_battery:
            return
        elif self.show_battery:
            battery = psutil.sensors_battery()
            if battery is not None:
                percent = battery.percent
                self.battery_percent.config(text=str(percent) + "%")
                self.battery_label.config(image=self.battery_icon)
            else:
                self.battery_percent.config(text="N/A")
                self.battery_label.config(image=self.battery_icon)
        else:
            self.battery_percent.config(text="")
            self.battery_label.config(image="")
        self.after(60000, self.update_battery)

    def update_weather(self):
        weather_data = self.get_weather_data(os.environ.get("API_KEY"), "50.8504", "4.3488")
        temperature = weather_data['temperature']
        temperature = round(temperature - 273.15)

        weather_icon = self.get_weather_icon(weather_data['weather'][0]['main'])
        self.weather_icon = Image.open(weather_icon).resize((40, 30))
        self.weather_icon = ImageTk.PhotoImage(self.weather_icon)
        self.weather_label.config(image=self.weather_icon)

        self.weather_temperature.config(text=f"{temperature}°C")
        self.after(160000, self.update_weather)
    
    def get_weather_icon(self, weather):
        if datetime.now().hour >= 21:
            return "assets/moon.png"
        elif weather == "Clear":
            return "assets/sun.png"
        elif weather == "Rain":
            return "assets/rain.png"
        elif weather == "Clouds":
            return "assets/clouds.png"
        else:
            return "assets/sun.png"

    def get_weather_data(self, api_key, lat, lon):
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
        response = requests.get(url)
        data = response.json()
        temperature = data['main']['temp']
        weather = data['weather']
        return {"temperature": temperature, "weather": weather}

    def on_drag_start(self, event):
        if not self.locked:
            self.start_x = event.x
            self.start_y = event.y

    def on_drag_motion(self, event):
        if not self.locked:
            delta_x = event.x - self.start_x
            delta_y = event.y - self.start_y

            self.geometry(f"+{self.winfo_x() + delta_x}+{self.winfo_y() + delta_y}")

    def on_drag_release(self, event):
        if not self.locked:
            self.start_x = 0
            self.start_y = 0

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def change_city(self):
        pass

    def change_opacity(self):
        pass

    def toggle_battery(self):
        self.show_battery = not self.show_battery
        if not self.show_battery:
            self.battery_percent.config(text="")
            self.battery_label.config(image="")
        else:
            self.update_battery()

    def lock(self):
        self.locked = True
        self.context_menu.delete(0, tk.END)
        self.context_menu.add_command(label="Unlock", command=self.unlock)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Quit", command=self.close_window)

    def unlock(self):
        self.locked = False
        self.context_menu.delete(0, tk.END)
        self.context_menu.add_command(label="Lock", command=self.lock)
        self.context_menu.add_command(label="Change City", command=self.change_city)
        self.context_menu.add_command(label="Change Opacity", command=self.change_opacity)
        self.context_menu.add_command(label="Display Battery", command=self.toggle_battery)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Quit", command=self.close_window)

    def close_window(self):
        self.destroy()

if __name__ == "__main__":
    app = TinyTaskbar()
    app.mainloop()