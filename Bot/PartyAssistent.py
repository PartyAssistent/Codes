# -*- coding: utf-8 -*-
#
# 2019-12-08 Caro Peist
# Installieren mit "pip install python-telegram-bot"
#
# Name: PartyAssistent
# Username: PartyAssistent_bot
# Token: 981489247:AAGWtWefLob7wBFwS3Ubchi-9wGaZECqnV8
#
# t.me/PartyAssistent.bot
#
import threading
import time
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
token = '981489247:AAGWtWefLob7wBFwS3Ubchi-9wGaZECqnV8'
 
 
def readPromille():
    return open('sensor_resultat.txt').read()

 
# Thread f�r die automatische Antwort
# L�uft endlos!
class MyThread(threading.Thread):
 
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.chat_id = None
        self.context = None
        self.stopp_spamming = False  # Stop-Flag
        self.username = None  # z. B.'Caro'
        self.useraddress = None  # z. B.'Berlin'
 
    def run(self):
        while True:
            time.sleep(15)  # Sekunden Wiederholzeit
 
            if self.stopp_spamming:
                text = 'OK {name}, sweet Dreams'
                text = text.format(name=self.username)
                self.context.bot.send_message(chat_id=self.chat_id, text=text)
                return  # Thread wird beendet
 
            if self.username is None or self.useraddress is None:
                continue
            
            try: 
                promille = readPromille()  # Gibt Text zurück
                promille = float(promille) # Klappt nur, wenn in der Datei das richtige Format steht, z.B. 0.8
            except Exception as exc: 
                text = 'Sensordaten fehlerhaft: {}.'.format(exc)
                self.context.bot.send_message(chat_id=self.chat_id, text=text)
                return 
            

            text = 'Hey {name}, bitte puste.'
            text = text.format(name=self.username)
            self.context.bot.send_message(chat_id=self.chat_id, text=text) #wird beides nicht ausgegeben, soll getrennt sein  mit kurzer Pause
            text = ' Du hast aktuell {promille} Promille! '
            text = text.format( promille=promille) 
            self.context.bot.send_message(chat_id=self.chat_id, text=text)
 
            if promille <= 0.3:
                text += 'Alles im grünen Bereich! Trinke demnächst mal ein nichtalkoholisches Getränk.'
            elif promille <= 0.8:
                text += 'Lasse dein Auto stehen! Nimm Öffis oder gönn dir ein Taxi: "030 202020"'
            elif promille <= 1.0:
                text += 'Denk dran stayhydrated, trink ein Glas Wasser.'
            elif promille <= 1.3:
                text += 'Leg eine Alkoholpause ein!'
            elif promille <= 1.5:
                text += 'Es wird langsam Zeit zu gehen. Lass die Finger vom Alkohol für heute. Morgen ist auch noch ein Tag ;)'
            elif promille <= 2.0:
                text += 'Auf nach Hause! Für dich ist die Party vorbei. Lass dein Auto stehen! Nimm Öffis oder gönn dir ein Taxi: "030 202020"'
            else:
                text += 'Uiuiui'
 
            self.context.bot.send_message(chat_id=self.chat_id, text=text)
 
 
my_thread = MyThread()
# Ende Threadklasse
 

# Bei jedem neuen Chat starten wir einen Thread. Trotzdem ist das aktuell
# NICHT mehrbenutzerfähig! Es läuft so nur mit genau einem aktiven Chat!!
def start(update, context):
    if my_thread.isAlive():
        text = ('PartyAssistent wird schon von {name} verwendet. Leider musst '
                'du die Party ohne mich durchstehen')
        text = text.format(name=my_thread.username)
    else:
        text = 'Hallo, ich bin dein PartyAssistent! Wie heisst du?'
        my_thread.chat_id = update.effective_chat.id
        my_thread.context = context
        my_thread.start()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
 
 
def echo(update, context):
 
    global my_thread
 
    # Die erste Antwort nach dem Eröffnen des Chats interpretieren
    # wir als den Usernamen. Spätere Korrektur ist nicht vorgesehen.
    if my_thread.username is None:
        my_thread.username = update.message.text
        text = 'OK {name}, wohin willst du nach der Party?'
        text = text.format(name=my_thread.username)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return
 
    # Die zweite Antwort nach dem Eröffnen des Chats ist die Adresse.
    if my_thread.useraddress is None:
        my_thread.useraddress = update.message.text
        text = 'OK {name}, du willst nach {address}!'
        text = text.format(name=my_thread.username, address=my_thread.useraddress)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
 
    # Um die Nachfrage zum Pusten zu stoppen, reicht ein "Ende" oder ein
    # "ende" irgendwo in der Nachricht aus.
    if 'ende' in update.message.text.lower():
        my_thread.stopp_spamming = True  # Gibt dem Thread den Befehl, zu stoppen
 
 
echo_handler = MessageHandler(Filters.text, echo)
start_handler = CommandHandler('start', start)
updater = Updater(token=token, use_context=True)
updater.dispatcher.add_handler(start_handler)
updater.dispatcher.add_handler(echo_handler)
print('Start Polling...')
updater.start_polling()
print('OK')
 