import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import json
import time
import matplotlib.pyplot as plt


class AirQualityBot:
    def __init__(self, token):
        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)
        self.user_data = {}  # Dictionary to store user data (chat_id -> {rooms, name})

        self.initialize_bot()

    def initialize_bot(self):
        while True:
            try:
                MessageLoop(self.bot, {'chat': self.on_chat_message}).run_as_thread()
                print("Bot is running...")
                break
            except Exception as e:
                print(f"Error initializing bot: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        user_name = msg['from'].get('first_name', 'User')  # Get user's first name from Telegram

        if content_type == 'text':
            message = msg['text']
            if message == "/start":
                if chat_id in self.user_data:
                    self.bot.sendMessage(chat_id, f"Hello {user_name}! Welcome back!\n"
                                                f"Your rooms: {', '.join(map(str, self.user_data[chat_id]['rooms']) )}\n"
                                                "Use /control, /status, or /user_management to proceed.")
                else:
                    self.bot.sendMessage(chat_id, f"Hello {user_name}! I am your Air Quality Bot!\n"
                                                "It looks like you're not registered yet.\n"
                                                "Please use /user_management to register and add your rooms.")
            elif message == "/user_management":
                if chat_id in self.user_data:
                    self.bot.sendMessage(chat_id, f"{user_name}, you are already registered.\n"
                                                "Would you like to update your list of rooms?\n"
                                                "Please provide your rooms in the format:\n<room1> <room2> ...")
                    self.bot_listener = ("update_rooms", chat_id)
                else:
                    self.bot.sendMessage(chat_id, f"{user_name}, you need to register first.\n"
                                                "Please provide your details in the format:\n<room1> <room2> ...")
                    self.bot_listener = ("register", chat_id)
            elif message == "/control":
                if chat_id in self.user_data:
                    self.bot.sendMessage(chat_id, "Please specify the room(s) for the action (e.g., '1 2 3' or 'all').")
                    self.bot_listener = ("control_select_room", chat_id)
                else:
                    self.bot.sendMessage(chat_id, "You need to register first. Use /user_management to register.")
            elif message == "/status":
                if chat_id in self.user_data:
                    self.bot.sendMessage(chat_id, "Please specify the room(s) for the status (e.g., '1 2 3' or 'all').")
                    self.bot_listener = ("status_select_room", chat_id)
                else:
                    self.bot.sendMessage(chat_id, "You need to register first. Use /user_management to register.")
            elif hasattr(self, "bot_listener") and self.bot_listener[1] == chat_id:
                command = self.bot_listener[0]
                if command == "register":
                    self.handle_registration(chat_id, message, user_name)
                elif command == "update_rooms":
                    self.update_rooms(chat_id, message)
                elif command == "control_select_room":
                    self.validate_rooms(chat_id, message)
                elif command == "control_select_action":
                    self.handle_control_action(chat_id, message)
                    del self.bot_listener  # Only clear listener after processing the action
                elif command == "status_select_room":
                    self.validate_status_rooms(chat_id, message)
                elif command == "status_select_type":
                    self.handle_status_type(chat_id, message)
                    del self.bot_listener  # Only clear listener after processing the status
            else:
                self.bot.sendMessage(chat_id, "Unknown command. Use /start for available commands.")


    def validate_rooms(self, chat_id, rooms):
        try:
            registered_rooms = self.user_data[chat_id]['rooms']
            if rooms == "all":
                rooms = registered_rooms
            else:
                rooms = list(map(int, rooms.strip().split()))

            invalid_rooms = [room for room in rooms if room not in registered_rooms]
            if invalid_rooms:
                self.bot.sendMessage(chat_id, f"Please select one of your registered rooms. Invalid rooms: {', '.join(map(str, invalid_rooms))}")
                return

            # Store validated rooms in listener
            self.bot_listener = ("control_select_action", chat_id, rooms)

            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="open_window"), KeyboardButton(text="close_window")],
                    [KeyboardButton(text="activate_ventilation"), KeyboardButton(text="stop_ventilation")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            self.bot.sendMessage(chat_id, "Please choose an action:", reply_markup=keyboard)
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error validating rooms. Ensure your input is correct.\nError: {e}")

    def handle_control_action(self, chat_id, action):
        if action in ["open_window", "close_window", "activate_ventilation", "stop_ventilation"]:
            rooms = self.bot_listener[2]  # Retrieve validated rooms
            self.handle_control_room(chat_id, rooms, action)
        else:
            self.bot.sendMessage(chat_id, "Invalid action. Please choose one of the options provided.")

    def handle_control_room(self, chat_id, rooms, action):
        try:
            for room in rooms:
                # Simulate MQTT 
                # topic = f"school/room/{room}/control"
                # payload = json.dumps({"action": action})
                # self.mqtt_client.publish(topic, payload)

                # Debug message for the action
                self.bot.sendMessage(chat_id, f"Simulating MQTT: '{action}' action sent for room {room}.")
                self.bot.sendMessage(chat_id, f"DEBUG: '{action}' action completed for room {room}.")
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error executing action. Ensure room selection and action are correct.\nError: {e}")

    def handle_registration(self, chat_id, registration_details, user_name):
        try:
            rooms = list(map(int, registration_details.strip().split()))
            self.user_data[chat_id] = {"rooms": rooms, "name": user_name}
            self.bot.sendMessage(chat_id, f"Registration successful, {user_name}!\n"
                                        f"Your rooms: {', '.join(map(str, rooms))}")

            # Display options using a custom keyboard
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="/control"), KeyboardButton(text="/status")],
                    [KeyboardButton(text="/user_management")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            self.bot.sendMessage(chat_id, "Welcome! What would you like to do next?", reply_markup=keyboard)
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Registration failed. Ensure the format is correct:\n<room1> <room2> ...\nError: {e}")


    def update_rooms(self, chat_id, room_details):
        try:
            rooms = list(map(int, room_details.strip().split()))
            self.user_data[chat_id]["rooms"] = rooms
            self.bot.sendMessage(chat_id, f"Your room list has been updated!\nYour rooms: {', '.join(map(str, rooms))}")
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Failed to update rooms. Ensure the format is correct:\n<room1> <room2> ...\nError: {e}")

    def validate_status_rooms(self, chat_id, rooms):
        try:
            registered_rooms = self.user_data[chat_id]['rooms']
            if rooms == "all":
                rooms = registered_rooms
            else:
                rooms = list(map(int, rooms.strip().split()))

            invalid_rooms = [room for room in rooms if room not in registered_rooms]
            if invalid_rooms:
                self.bot.sendMessage(chat_id, f"Please select one of your registered rooms. Invalid rooms: {', '.join(map(str, invalid_rooms))}")
                return

            # Store validated rooms in listener
            self.bot_listener = ("status_select_type", chat_id, rooms)

            # Display status options using a nice keyboard
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="present_status"), KeyboardButton(text="daily_status")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            self.bot.sendMessage(chat_id, "Please choose a status type:", reply_markup=keyboard)
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error validating rooms. Ensure your input is correct.\nError: {e}")

    def handle_status_type(self, chat_id, status_type):
        if status_type in ["present_status", "daily_status"]:
            rooms = self.bot_listener[2]  # Retrieve validated rooms
            self.handle_status_room(chat_id, rooms, status_type)
        else:
            self.bot.sendMessage(chat_id, "Invalid status type. Please choose one of the options provided.")

    def handle_status_room(self, chat_id, rooms, status_type):
        try:
            for room in rooms:
                if status_type == "present_status":
                    # Uncomment to MQTT
                    """
                    topic = f"school/room/{room}/status"
                    payload = json.dumps({"action": "get_present_status"})
                    self.mqtt_client.publish(topic, payload)

                    # Placeholder for MQTT subscription and response handling
                    def on_message(client, userdata, msg):
                        present_status = json.loads(msg.payload.decode())
                        self.bot.sendMessage(chat_id, f"Room {room}: {present_status['message']}")

                    self.mqtt_client.subscribe(topic)
                    self.mqtt_client.on_message = on_message
                    """
                    # Debug message
                    self.bot.sendMessage(chat_id, f"Room {room}: DEBUG: Present status fetched successfully. (Simulated)")
                elif status_type == "daily_status":
                    # Placeholder for MQTT logic to fetch daily statistics
                    """
                    topic = f"school/room/{room}/daily_statistics"
                    payload = json.dumps({"action": "get_daily_statistics"})
                    self.mqtt_client.publish(topic, payload)

                    # Placeholder for MQTT subscription and handling the received data
                    def on_message(client, userdata, msg):
                        daily_data = json.loads(msg.payload.decode())
                        self.generate_daily_graph(chat_id, room, daily_data)

                    self.mqtt_client.subscribe(topic)
                    self.mqtt_client.on_message = on_message
                    """

                    # For now, simulate the daily statistics using the local JSON file
                    if room == 1:  # Toy example for Room 1
                        try:
                            with open("daily_status.json", "r") as file:
                                daily_data = json.load(file)
                            self.generate_daily_graph(chat_id, room, daily_data)
                        except FileNotFoundError:
                            self.bot.sendMessage(chat_id, "Error: Daily statistics file not found.")
                        except json.JSONDecodeError:
                            self.bot.sendMessage(chat_id, "Error: Could not decode daily statistics data.")
                    else:
                        self.bot.sendMessage(chat_id, f"Room {room}: Daily statistics not available in the toy example.")
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error fetching status for rooms {rooms}. Ensure room selection is correct.\nError: {e}")


    def generate_daily_graph(self, chat_id, room, daily_data):
        try:
            hours = [data["hour"] for data in daily_data]
            air_quality = [data["air_quality"] for data in daily_data]

            plt.figure(figsize=(10, 6))
            plt.plot(hours, air_quality, marker="o", linestyle="-", label=f"Room {room}")
            plt.title(f"Daily Air Quality for Room {room}", fontsize=16)
            plt.xlabel("Hour of the Day", fontsize=12)
            plt.ylabel("Air Quality (1=Very Good, 5=Very Poor)", fontsize=12)
            plt.xticks(hours)
            plt.grid(True)
            plt.legend()

            file_name = f"daily_air_quality_room_{room}_{chat_id}.png"
            plt.savefig(file_name)
            plt.close()

            with open(file_name, "rb") as photo:
                self.bot.sendPhoto(chat_id, photo)
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error plotting daily graph for Room {room}: {e}")


    def plot_daily_graph(self, chat_id, daily_data, room):
        try:
            hours = [data["hour"] for data in daily_data]
            air_quality = [data["air_quality"] for data in daily_data]

            plt.figure(figsize=(10, 6))
            plt.plot(hours, air_quality, marker="o", linestyle="-", label=f"Room {room}")
            plt.title(f"Daily Air Quality for Room {room}", fontsize=16)
            plt.xlabel("Hour of the Day", fontsize=12)
            plt.ylabel("Air Quality (1=Very Good, 5=Very Poor)", fontsize=12)
            plt.xticks(hours)
            plt.grid(True)
            plt.legend()

            file_name = f"daily_air_quality_room_{room}_{chat_id}.png"
            plt.savefig(file_name)
            plt.close()

            with open(file_name, "rb") as photo:
                self.bot.sendPhoto(chat_id, photo)
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error plotting daily graph for Room {room}: {e}")


# Load bot token from JSON file
with open("bot_token.json", "r") as file:
    data = json.load(file)

# Initialize bot
bot_instance = AirQualityBot(data["telegramToken"])

# Keep bot alive
while True:
    time.sleep(10)
