from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox
from tkinter import filedialog
import xlsxwriter
import os
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import keras
from keras.models import Sequential
from keras.models import model_from_json
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

root = Tk()
root.title("Ethanol production simulator")
root.iconbitmap('ethanol.ico')

class MyApp:
###############################################
############### MAIN WINDOW ###################
###############################################
    def __init__(self, parent):
        w = 860  # width for the Tk root
        h = 245  # height for the Tk root
        # get screen width and height
        ws = parent.winfo_screenwidth()  # width of the screen
        hs = parent.winfo_screenheight()  # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        # set the dimensions of the screen
        # and where it is placed
        parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

        self.data_value=list()
        self.fr = Frame(parent, padx=60, pady=60).grid()
        self.bt0 = Label(self.fr, text='INSERT TIMESTEPS:', bg='grey', padx=30, pady=5, relief=RIDGE).grid(row=0, column=0, sticky='ew', ipadx=3, ipady=3)
        self.e = Entry(self.fr, bg='white')
        self.e.grid(row=0, column=1, sticky='ew', ipadx=3, ipady=3)
        self.bt1 = Button(self.fr, text='CREATE SPREADSHEET', bg='grey', padx=30, pady=5, relief=RIDGE, command=self.data_window).grid(row=1, column=0, columnspan=2, sticky='ew', ipadx=3, ipady=3)
        self.bt3 = Button(self.fr, text='OFFLINE SIMULATION', bg='grey', padx=30, pady=5, command=self.offline_simulation, relief=RIDGE).grid(row=3, column=0, sticky='ew', columnspan=2)
        self.bt4 = Button(self.fr, text='OPEN IMAGENS', bg='grey', padx=30, pady=5, command=self.open_img, relief=RIDGE).grid(row=4, column=0, sticky='ew', columnspan=2)
        self.bt5 = Button(self.fr, text='SAVE SIMULATED DATA', bg='grey', padx=30, pady=5, relief=RIDGE, command=self.save_simulated_data).grid(row=5, column=0, sticky='ew', columnspan=2)
        self.bt6 = Button(self.fr, text='UPLOAD RNN-LSTM MODEL', bg='grey', padx=30, pady=5, command=self.upload_model, relief=RIDGE).grid(row=2, column=0, sticky='ew', columnspan=2)
        self.bt7 = Button(self.fr, text='TRAIN RNN-LSTM MODEL', bg='grey', padx=30, pady=5, relief=RIDGE, command=self.train).grid(row=6, column=0, sticky='ew', columnspan=2)
        self.lb = Label(self.fr, text="The number of samples required by this program depends on the number of timesteps \n"
                                      "used by the RNN-LSTM developed. V, X, S, P, Qin, Sin, Xin temporally spaced in 1 h. \n"
                            "Use the CREATE SPREADSHEET button to create one and save the data.\n ", bg='white', padx=50)
        self.lb.grid(row=0, column=2, rowspan=7, sticky=E+W+N+S)
#__________FUNCTIONS

#############################################################
####################### CREATE SPREADSHEET ##################
#############################################################
    def data_window(self):
        self.win = Toplevel()
        self.win.title("DATA WINDOW")

        Label(self.win, text="V (L)", bg='grey', padx=10, pady=5, relief=RIDGE).grid(row=0, column=0, sticky=E+W)
        Label(self.win, text="X (g/L)", bg='grey', padx=10, pady=5, relief=RIDGE).grid(row=0, column=1, sticky=E+W)
        Label(self.win, text="S (g/L)", bg='grey', padx=10, pady=5, relief=RIDGE).grid(row=0, column=2, sticky=E+W)
        Label(self.win, text="P (g/L)", bg='grey', padx=10, pady=5, relief=RIDGE).grid(row=0, column=3, sticky=E+W)
        Label(self.win, text="Qin (L/h)", bg='grey', padx=10, pady=5, relief=RIDGE).grid(row=0, column=4, sticky=E+W)
        Label(self.win, text="Xin (g/L)", bg='grey', padx=10, pady=5, relief=RIDGE).grid(row=0, column=6, sticky=E+W)
        Label(self.win, text="Sin (g/L)", bg='grey', padx=10, pady=5, relief=RIDGE).grid(row=0, column=5, sticky=E+W)

        V_ent, X_ent, S_ent, P_ent, Qin_ent, Xin_ent, Sin_ent = [], [], [], [], [], [], []
        for i in range(int(self.e.get())):
            V_ent.append(Entry(self.win, bg='white'))
            X_ent.append(Entry(self.win, bg='white'))
            S_ent.append(Entry(self.win, bg='white'))
            P_ent.append(Entry(self.win, bg='white'))
            Qin_ent.append(Entry(self.win, bg='white'))
            Xin_ent.append(Entry(self.win, bg='white'))
            Sin_ent.append(Entry(self.win, bg='white'))

            V_ent[i].grid(row=i+1, column=0, sticky=E+W)
            X_ent[i].grid(row=i+1, column=1, sticky=E+W)
            S_ent[i].grid(row=i+1, column=2, sticky=E+W)
            P_ent[i].grid(row=i+1, column=3, sticky=E+W)
            Qin_ent[i].grid(row=i+1, column=4, sticky=E+W)
            Xin_ent[i].grid(row=i+1, column=6, sticky=E+W)
            Sin_ent[i].grid(row=i+1, column=5, sticky=E+W)

        i=int(self.e.get())+2
        self.get_data_button = Button(self.win, text="GET DATA FROM AN EXCEL SPREADSHEET", bg='grey', relief=RIDGE)
        self.get_data_button.configure(command=self.open_spreadsheet)
        self.get_data_button.grid(row=i, column=0, columnspan=2, sticky=W+E)
        self.create_initial_spreadsheet = Button(self.win, text="CREATE INITIAL EXCEL SPREADSHEET", bg='grey', relief=RIDGE)
        self.create_initial_spreadsheet.configure(command=self.create_initial)
        self.create_initial_spreadsheet.grid(row=i, column=2, columnspan=3, sticky=W + E)
        self.save_data_button = Button(self.win, text="SAVE DATA FOR SIMULATION", bg='grey', relief=RIDGE)
        self.save_data_button.configure(command=self.save_data_for_offline_simulation)
        self.save_data_button.grid(row=i, column=5, columnspan=2, sticky=W+E)

    def create_initial(self):
        directory = filedialog.askdirectory(title="Select the directory to save the file")
        directory = str(directory+'/Initial_spreadsheet.xlsx')
        workbook = xlsxwriter.Workbook(directory)
        worksheet = workbook.add_worksheet()
        worksheet.write('A1', 'V (L)')
        worksheet.write('B1', 'X (g/L)')
        worksheet.write('C1', 'S (g/L)')
        worksheet.write('D1', 'P (g/L)')
        worksheet.write('E1', 'Qin (L/h)')
        worksheet.write('G1', 'Xin (g/L)')
        worksheet.write('F1', 'Sin (g/L)')
        workbook.close()

    def open_spreadsheet(self):
        root.filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select A Spreadsheet File", filetypes=(("Excel files", ".xls"), ("Excel files", ".xlsx")))
        data = pd.read_excel(root.filename)
        self.data_value = data.values.tolist()
        V_ent, X_ent, S_ent, P_ent, Qin_ent, Xin_ent, Sin_ent = [], [], [], [], [], [], []
        index=int(len(self.data_value)-int(self.e.get()))
        for i in range(int(self.e.get())):
            V_ent.append(Entry(self.win, bg='white'))
            X_ent.append(Entry(self.win, bg='white'))
            S_ent.append(Entry(self.win, bg='white'))
            P_ent.append(Entry(self.win, bg='white'))
            Qin_ent.append(Entry(self.win, bg='white'))
            Xin_ent.append(Entry(self.win, bg='white'))
            Sin_ent.append(Entry(self.win, bg='white'))

            V_ent[i].insert(0, float(self.data_value[index+i][0]))
            X_ent[i].insert(0, float(self.data_value[index+i][1]))
            S_ent[i].insert(0, float(self.data_value[index+i][2]))
            P_ent[i].insert(0, float(self.data_value[index+i][3]))
            Qin_ent[i].insert(0, float(self.data_value[index+i][4]))
            Sin_ent[i].insert(0, float(self.data_value[index+i][5]))
            Xin_ent[i].insert(0, float(self.data_value[index+i][6]))

            V_ent[i].grid(row=i + 1, column=0, sticky=E + W)
            X_ent[i].grid(row=i + 1, column=1, sticky=E + W)
            S_ent[i].grid(row=i + 1, column=2, sticky=E + W)
            P_ent[i].grid(row=i + 1, column=3, sticky=E + W)
            Qin_ent[i].grid(row=i + 1, column=4, sticky=E + W)
            Sin_ent[i].grid(row=i + 1, column=5, sticky=E + W)
            Xin_ent[i].grid(row=i + 1, column=6, sticky=E + W)

    def save_data_for_offline_simulation(self):
        messagebox.showinfo("INFO", "Data saved for offline simulation")
        self.win.destroy()
        init = int(len(self.data_value)-int(self.e.get()))
        final = int(len(self.data_value))
        for i in range(int(self.e.get())):
            out = self.norm(self.data_value[init+i][0], self.data_value[init+i][1], self.data_value[init+i][2], self.data_value[init+i][3],
                            self.data_value[init+i][4], self.data_value[init+i][5], self.data_value[init+i][6])
            self.data_value[i][0] = out[0]
            self.data_value[i][1] = out[1]
            self.data_value[i][2] = out[2]
            self.data_value[i][3] = out[3]
            self.data_value[i][4] = out[4]
            self.data_value[i][5] = out[5]
            self.data_value[i][6] = out[6]
        self.data_value = self.data_value[init:final][:]
        self.x_offline = np.reshape(self.data_value, (1, int(self.e.get()), 7))
#############################################################
####################### OFFLINE SIMULATION ##################
#############################################################
    def denorm(self, V_norm, X_norm, S_norm, P_norm):
        max = [4.53752893, 0.17307039, 118.70447215, 16.49197396]
        min = [1.30787382,  0.04834902, 0,  4.39536337]
        V = V_norm*(max[0]-min[0])+min[0]
        X = X_norm*(max[1]-min[1])+min[1]
        S = S_norm*(max[2]-min[2])+min[2]
        P = P_norm*(max[3]-min[3])+min[3]
        return [V, X, S, P]

    def norm(self, V, X, S, P, Q, Si, Xi):
        max = [4.53752893, 0.17307039, 118.70447215, 16.49197396, 0.1086, 150, 0.075]
        min = [1.30787382,  0.04834902, 0,  4.39536337, 0.057, 50, 0.025]
        V_norm = 1-(max[0]-V)/(max[0]-min[0])
        X_norm = 1-(max[1]-X)/(max[1]-min[1])
        S_norm = 1-(max[2]-S)/(max[2]-min[2])
        P_norm = 1-(max[3]-P)/(max[3]-min[3])
        Q_norm = 1-(max[4]-Q)/(max[4]-min[4])
        Si_norm = 1-(max[5]-Si)/(max[5]-min[5])
        Xi_norm = 1-(max[6]-Xi)/(max[6]-min[6])

        return [V_norm, X_norm, S_norm, P_norm, Q_norm, Si_norm, Xi_norm]

    def offline_simulation(self):
        look_back = int(self.e.get())
        ni = 7
        no = 4
        x_offline = self.data_value
        x_offline = np.reshape(x_offline, (1, look_back, ni))
        y_data_offline = []

        for i in range(50):
            y_predict_offline = self.regressor.predict(x_offline, batch_size=None, verbose=0)
            x_data = np.delete(x_offline, 0, 1)
            new_line = np.array([y_predict_offline[0,0], y_predict_offline[0,1], y_predict_offline[0,2], y_predict_offline[0,3], self.data_value[-1][4], self.data_value[-1][5], self.data_value[-1][6]])
            x_data = np.reshape(x_data, [look_back-1, ni])
            new_line = np.reshape(new_line, [1, ni])
            x_data = np.concatenate([x_data, new_line])
            x_offline = np.reshape(x_data, (1, look_back, ni))
            y_data_offline.append(y_predict_offline)
        y_offline = np.reshape(y_data_offline, [-1, no])
        self.v, self.x, self.s, self.p = [], [], [], []
        for i in range(len(y_offline)):
            out = self.denorm(y_offline[i][0], y_offline[i][1], y_offline[i][2], y_offline[i][3])
            self.v.append(out[0]), self.x.append(out[1]), self.s.append(out[2]), self.p.append(out[3])
        messagebox.showinfo("OFFLINE SIMULATION", "The simulation has finished.")
        self.tempo = np.linspace(0, int(3 * len(self.v) - 3), int(len(self.v)))
############################################################
#######################  IMAGE WINDOW #######################
#############################################################
    def save_images(self):
        directory = filedialog.askdirectory(title="Select the directory to save the images")
        self.directory1 = str(directory + '/V.png')
        self.directory2 = str(directory + '/X.png')
        self.directory3 = str(directory + '/S.png')
        self.directory4 = str(directory + '/P.png')
        self.tempo = np.linspace(0, int(3*len(self.v)-3), int(len(self.v)))
        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('V (L)')
        plt.plot(self.tempo, self.v, color='k', linewidth=2)
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory1, dpi=600)
        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('X (g/L)')
        plt.plot(self.tempo, self.x, color='k', linewidth=2)
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory2, dpi=600)
        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('S (g/L)')
        plt.plot(self.tempo, self.s, color='k', linewidth=2)
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory3, dpi=600)
        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('P (g/L)')
        plt.plot(self.tempo, self.p, color='k', label='Real', linewidth=2)
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory4, dpi=600)
        self.btw3['bg'] = 'grey'
        self.btw4['bg'] = 'grey'
        self.btw5['bg'] = 'grey'
        self.btw6['bg'] = 'grey'

    def open_img(self):
        self.top = Toplevel()
        self.top.title("OFFLINE SIMULATION")
        self.deathwing = Image.open('logolcap.png')
        self.image2 = self.deathwing.resize((320, 210), Image.ANTIALIAS)
        self.Deathwing2 = ImageTk.PhotoImage(self.image2)
        self.lb1 = Label(self.top, image=self.Deathwing2).grid(row=0, column=0, columnspan=5, sticky=E + W)
        self.btw1 = Button(self.top, command=self.save_images, padx=15, pady=5)
        self.btw1.configure(text='SAVE IMAGE', bg='grey')
        self.btw1.grid(row=1, column=0, sticky=W+E)

        self.btw3 = Button(self.top, command=self.click_v, padx=15, pady=5)
        self.btw3.configure(text='V', background='grey')
        self.btw3.grid(row=1, column=1, sticky=W+E)

        self.btw4 = Button(self.top, command=self.click_x, padx=15, pady=5)
        self.btw4.configure(text='X', bg='grey')
        self.btw4.grid(row=1, column=2, sticky=W + E)

        self.btw5 = Button(self.top, command=self.click_s, padx=15, pady=5)
        self.btw5.configure(text='S', bg='grey')
        self.btw5.grid(row=1, column=3, sticky=W + E)

        self.btw6 = Button(self.top, command=self.click_p,padx=15, pady=5)
        self.btw6.configure(text='P', bg='grey')
        self.btw6.grid(row=1, column=4, sticky=W+E)

    def click_v(self):
        if self.btw3['bg'] == 'grey':
            self.btw3['bg'] = 'blue'
            self.btw4['bg'] = 'grey'
            self.btw5['bg'] = 'grey'
            self.btw6['bg'] = 'grey'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('V (L)')
            plt.plot(self.tempo, self.v, color='k', linewidth=2)
            plt.grid('True')
            plt.tight_layout()
            plt.show()
    def click_x(self):
        if self.btw4['bg'] == 'grey':
            self.btw3['bg'] = 'grey'
            self.btw4['bg'] = 'blue'
            self.btw5['bg'] = 'grey'
            self.btw6['bg'] = 'grey'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('X (g/L)')
            plt.plot(self.tempo, self.x, color='k', linewidth=2)
            plt.grid('True')
            plt.tight_layout()
            plt.show()

    def click_s(self):
        if self.btw5['bg'] == 'grey':
            self.btw3['bg'] = 'grey'
            self.btw4['bg'] = 'grey'
            self.btw5['bg'] = 'blue'
            self.btw6['bg'] = 'grey'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('S (g/L)')
            plt.plot(self.tempo, self.s, color='k', linewidth=2)
            plt.grid('True')
            plt.tight_layout()
            plt.show()

    def click_p(self):
        if self.btw6['bg'] == 'grey':
            self.btw3['bg'] = 'grey'
            self.btw4['bg'] = 'grey'
            self.btw5['bg'] = 'grey'
            self.btw6['bg'] = 'blue'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('P (g/L)')
            plt.plot(self.tempo, self.p, color='k', label='Real', linewidth=2)
            plt.grid('True')
            plt.tight_layout()
            plt.show()

#############################################################
####################### SAVE SIMULATED DATA #################
#############################################################
    def save_simulated_data(self):
        directory = filedialog.askdirectory(title="Select the directory to save the file")
        directory = str(directory + '/simulated_data.xlsx')
        workbook = xlsxwriter.Workbook(directory)
        worksheet = workbook.add_worksheet()
        worksheet.write('A1', 'V (L)')
        worksheet.write('B1', 'X (g/L)')
        worksheet.write('C1', 'S (g/L)')
        worksheet.write('D1', 'P (g/L)')
        for i in range(len(self.v)):
            worksheet.write(i+1, 0, float(self.v[i]))
            worksheet.write(i+1, 1, float(self.x[i]))
            worksheet.write(i+1, 2, float(self.s[i]))
            worksheet.write(i+1, 3, float(self.p[i]))
        workbook.close()
#############################################################
#################### UPLOAD RNN-LSTM MODEL ##################
#############################################################
    def upload_model(self):
        root.filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select The RNN-LSTM model", filetypes=[("JSON File", "*.json")])
        json_file = open(root.filename, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.regressor = model_from_json(loaded_model_json)
        root.filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select model weights", filetypes=[("H5 File", "*.h5")])
        self.regressor.load_weights(root.filename)
        messagebox.showinfo("INFO", "MODEL UPLOADED SUCCESSFULLY")

##############################################
################## TRAINING ##################
##############################################

    def train(self):
        self.top_train = Toplevel()
        self.top_train.geometry('+%d+%d'%(0,0))
        self.top_train.title("TRAINING RNN-LSTM MODEL")
        self.timesteps = Entry(self.top_train, bg='white', text='TIMESTEPS')
        self.neurons = Entry(self.top_train, bg='white', text='NEURONS')
        self.l1 = Entry(self.top_train, bg='white', text='L1')
        self.l2 = Entry(self.top_train, bg='white', text='L2')
        self.dropout = Entry(self.top_train, bg='white', text='DROPOUT')
        self.init_mode = Entry(self.top_train, bg='white', text='INIT_MODE')
        self.f_train = Entry(self.top_train, bg='white', text='TRAIN-TEST SPLIT')
        self.en = Entry(self.top_train, bg='white', text='EPOCHS')
        self.bs = Entry(self.top_train, bg='white', text='BATCH SIZE')
        self.vs = Entry(self.top_train, bg='white', text='VALIDATION SPLIT')
        self.patience = Entry(self.top_train, bg='white', text='PATIENCE')

        Label(self.top_train, bg='grey', text='TIMESTEPS', padx=9, pady=5, relief=RIDGE).grid(row=0, column=0, sticky=N+S+W+E)
        Label(self.top_train, bg='grey', text='NEURONS', padx=9, pady=5, relief=RIDGE).grid(row=1, column=0, sticky=N+S+W+E)
        Label(self.top_train, bg='grey', text='L1', padx=9, pady=5, relief=RIDGE).grid(row=2, column=0, sticky=N+S+W+E)
        Label(self.top_train, bg='grey', text='L2', padx=9, pady=5, relief=RIDGE).grid(row=3, column=0, sticky=N+S+W+E)
        Label(self.top_train, bg='grey', text='DROPOUT', padx=9, pady=5, relief=RIDGE).grid(row=4, column=0, sticky=N+S+W+E)
        Label(self.top_train, bg='grey', text='INIT_MODE', padx=9, pady=5, relief=RIDGE).grid(row=5, column=0, sticky=N+S+W+E)
        Label(self.top_train, bg='grey', text='TRAIN-TEST SPLIT', padx=9, pady=5, relief=RIDGE).grid(row=6, column=0, sticky=N+S+W+E)
        Label(self.top_train, bg='grey', text='EPOCHS', padx=9, pady=5, relief=RIDGE).grid(row=7, column=0, sticky=N+S+W+E)
        Label(self.top_train, bg='grey', text='BATCH SIZE', padx=9, pady=5, relief=RIDGE).grid(row=8, column=0, sticky=N+S+W+E)
        Label(self.top_train, bg='grey', text='VALIDATION SPLIT', padx=9, pady=5, relief=RIDGE).grid(row=9, column=0, sticky=N+S+W+E)
        Label(self.top_train, bg='grey', text='PATIENCE', padx=9, pady=5, relief=RIDGE).grid(row=10, column=0, sticky=N+S+W+E)

        self.timesteps.grid(row=0, column=1, sticky=N+S+W+E, columnspan=2)
        self.neurons.grid(row=1, column=1, sticky=N+S+W+E, columnspan=2)
        self.l1.grid(row=2, column=1, sticky=N+S+W+E, columnspan=2)
        self.l2.grid(row=3, column=1, sticky=N+S+W+E, columnspan=2)
        self.dropout.grid(row=4, column=1, sticky=N+S+W+E, columnspan=2)
        self.init_mode.grid(row=5, column=1, sticky=N+S+W+E, columnspan=2)
        self.f_train.grid(row=6, column=1, ipadx=20, ipady=5, sticky=N+S+W+E, columnspan=2)
        self.en.grid(row=7, column=1, sticky=N+S+W+E, columnspan=2)
        self.bs.grid(row=8, column=1, sticky=N+S+W+E, columnspan=2)
        self.vs.grid(row=9, column=1, sticky=N+S+W+E, columnspan=2)
        self.patience.grid(row=10, column=1, sticky=N+S+W+E, columnspan=2)

        self.bt_train_LSTM = Button(self.top_train, command=self.train_LSTM)
        self.bt_train_LSTM.configure(bg='green', padx=9, pady=5, relief=RIDGE, text='Train RNN-LSTM model')
        self.bt_train_LSTM.grid(row=11, column=0, sticky=W+E+S+N, columnspan=1)
        self.bt_save_LSTM = Button(self.top_train)
        self.bt_save_LSTM.configure(bg='green', padx=9, pady=5, relief=RIDGE, text='Save RNN-LSTM model')
        self.bt_save_LSTM.grid(row=11, column=1, sticky=W + E + S + N, columnspan=1)
        self.bt_help_LSTM = Button(self.top_train, command=self.help_LSTM)
        self.bt_help_LSTM.configure(bg='green', padx=9, pady=5, relief=RIDGE, text='HELP')
        self.bt_help_LSTM.grid(row=11, column=2, sticky=W + E + S + N, columnspan=1)

    def train_LSTM(self):
        root.filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select A Spreadsheet File Containing the Dataset.",
                                               filetypes=(("Excel files", ".xls"), ("Excel files", ".xlsx")))
        dataset_train = pd.read_excel(root.filename, 'Sheet1', index_col=None)
        self.data_value = dataset_train.values.tolist()

        # Variáveis Auxiliares
        look_back = int(self.timesteps.get())
        neurons = int(self.neurons.get())
        l1 = float(self.l1.get())
        l2 = float(self.l2.get())
        do = float(self.dropout.get())
        init_mode = str(self.init_mode.get())
        np.random.seed(1)  # reproducibility
        ni = 7  # number of input variables
        no = 4  # number of output variables
        f_train = float(self.f_train.get())  # fraction of dataset used in the training stage
        en = int(self.en.get())  # epochs
        bs = int(self.bs.get())  # batch size
        vs = float(self.vs.get())  # validation split percentage
        patience = int(self.patience.get())  # early stopping check number

        # Creating a data structure with look_back timesteps and 1 output
        def create_dataset(training_set_scaled, look_back):
            x_train, y_train = [], []
            for i in range(look_back, len(training_set_scaled)):
                x_train.append(training_set_scaled[i - look_back:i, 0:ni + 1])
                y_train.append(training_set_scaled[i, 0:no])
            return np.array(x_train), np.array(y_train)

        training_set = dataset_train.iloc[:, 1:8].values  # column 0 is time

        ## Feature scaling
        sc = MinMaxScaler(feature_range=(0, 1))
        output = MinMaxScaler(feature_range=(0, 1))
        training_set_scaled = sc.fit_transform(training_set)
        output_scaled = output.fit_transform(np.reshape(training_set[:, 0:no], [-1, no]))

        ## Split into train and test sets
        train_size = int(len(training_set_scaled) * f_train)
        test_size = len(training_set_scaled) - train_size
        training_set_splited = training_set_scaled[0:train_size, :]
        test_set_splited = training_set_scaled[train_size:len(training_set_scaled), :]
        x_train, y_train = create_dataset(training_set_splited, look_back)
        x_test, y_test = create_dataset(test_set_splited, look_back)

        # Definindo a rede
        self.regressor = Sequential()
        # 1st layer
        self.regressor.add(LSTM(units=neurons, input_shape=(look_back, ni), kernel_initializer=init_mode,
                           kernel_regularizer=keras.regularizers.l1_l2(l1=l1, l2=l2)))
        self.regressor.add(Dropout(do))
        # Adding the output layer
        self.regressor.add(Dense(units=no))
        # Compiling the RNN
        self.regressor.compile(optimizer='adam', loss='mean_squared_error')
        # simple early stopping and model checkpoint
        es = EarlyStopping(monitor='val_loss', mode='auto', verbose=0, patience=patience)
        mc = ModelCheckpoint('best_model.h5', monitor='val_loss', mode='auto', verbose=0, save_best_only=True)
        # Fitting the RNN to the training set
        self.history = self.regressor.fit(x_train, y_train, validation_split=vs, epochs=en, batch_size=bs, verbose=0,
                                callbacks=[es, mc])
        self.train_predict = self.regressor.predict(x_train, batch_size=None, verbose=0)
        self.regressor.reset_states()
        self.test_predict = self.regressor.predict(x_test, batch_size=None, verbose=0)
        self.trainScore = mean_squared_error(y_train, self.train_predict)
        self.testScore = mean_squared_error(y_test, self.test_predict)

        self.regressor.reset_states()
        # Initial data
        x_offline = training_set_scaled[0:look_back, :]
        x_offline = np.reshape(x_offline, (1, look_back, ni))
        y_data_offline = []

        for i in range(look_back, 50):
            y_predict_offline = self.regressor.predict(x_offline, batch_size=None, verbose=0)
            x_data = training_set_scaled[i - look_back + 1:i + 1, :]
            x_data[look_back - 1, 0:no] = y_predict_offline
            x_offline = np.reshape(x_data, (1, look_back, ni))
            y_data_offline.append(y_predict_offline)

        y_offline = np.reshape(y_data_offline, [-1, no])
        y_real = output_scaled[look_back:-1, 0:no]

        self.offlineScore = mean_squared_error(y_real, y_offline)
        self.y_offline = output.inverse_transform(y_offline)
        self.y_real = output.inverse_transform(y_real)

        self.train_predict = output.inverse_transform(self.train_predict)
        self.test_predict = output.inverse_transform(self.test_predict)
        self.y_train = output.inverse_transform(y_train)
        self.y_test = output.inverse_transform(y_test)

        self.bt_save_LSTM = Button(self.top_train, command=self.save_LSTM)
        self.bt_save_LSTM.configure(bg='green', padx=9, pady=5, relief=RIDGE, text='Save RNN-LSTM model')
        self.bt_save_LSTM.grid(row=11, column=1, sticky=W + E + S + N, columnspan=1)

        Label(self.top_train, text= "Train MSE", bg='green').grid(row=12, column=0, sticky=W + E + S + N)
        Label(self.top_train, text="Test MSE", bg='green').grid(row=13, column=0, sticky=W + E + S + N)
        Label(self.top_train, text="Offline MSE", bg='green').grid(row=14, column=0, sticky=W + E + S + N)
        Label(self.top_train, text=str(self.trainScore), bg='white').grid(row=12, column=1, sticky=W + E + S + N)
        Label(self.top_train, text=str(self.testScore), bg='white').grid(row=13, column=1, sticky=W + E + S + N)
        Label(self.top_train, text=str(self.offlineScore), bg='white').grid(row=14, column=1, sticky=W + E + S + N)
        self.bt_train_results = Button(self.top_train, command=self.train_results)
        self.bt_train_results.configure(bg='green', padx=9, pady=5, relief=RIDGE, text='SHOW TRAIN RESULTS')
        self.bt_train_results.grid(row=12, column=2, sticky=W + E + S + N, rowspan=3)

    def save_LSTM(self):
        directory = filedialog.askdirectory(title="Select the directory to save the file")
        directory1 = str(directory + '/model.json')
        directory2 = str(directory + '/model.h5')
        model_json = self.regressor.to_json()
        with open(directory1, "w") as json_file:
            json_file.write(model_json)
        self.regressor.save_weights(directory2)

    def help_LSTM(self):
        self.help_train = Toplevel()
        self.help_train.geometry('+%d+%d'%(400,0))
        self.help_train.title("HELP")
        Label(self.help_train, text="Timesteps", bg='yellow', padx=10, relief=RIDGE).grid(row=0, column=0, sticky=E+W+N+S)
        Label(self.help_train, anchor=W, text="Number of temporal data used as one example, it must be an integer", bg='white', relief=RIDGE).grid(row=0, column=1, sticky=E+W+N+S)
        Label(self.help_train, text="Neurons", bg='yellow', padx=10, relief=RIDGE).grid(row=1, column=0, sticky=E+W+N+S)
        Label(self.help_train, anchor=W, text="Number of neurons in each LSTM gate, it must be an integer", bg='white', relief=RIDGE).grid(row=1, column=1, sticky=E+W+N+S)
        Label(self.help_train, text="L1", bg='yellow', padx=10, relief=RIDGE).grid(row=2, column=0, sticky=E+W+N+S)
        Label(self.help_train, anchor=W, text="Weight for L1 regularization, it must be a float", bg='white', relief=RIDGE).grid(row=2, column=1, sticky=E+W+N+S)
        Label(self.help_train, text="L2", bg='yellow', padx=10, relief=RIDGE).grid(row=3, column=0, sticky=E+W+N+S)
        Label(self.help_train, anchor=W, text="Weight for L2 regularization, it must be a float", bg='white', relief=RIDGE).grid(row=3, column=1, sticky=E+W+N+S)
        Label(self.help_train, text="Dropout", bg='yellow', padx=10, relief=RIDGE).grid(row=4, column=0, sticky=E+W+N+S)
        Label(self.help_train, anchor=W, text="Percentage of dropout, it must be a float between 0 and 1", bg='white', relief=RIDGE).grid(row=4, column=1, sticky=E+W+N+S)
        Label(self.help_train, text="Init_mode", bg='yellow', padx=10, relief=RIDGE).grid(row=5, column=0, sticky=E+W+N+S)
        Label(self.help_train, text="Initial weight distribution, it must be a string \n"
                                    "viable options: random_uniform, random_normal, \n"
                                    "lecun_uniform, glorot_normal, ones, glorot_uniform, zeros, identity", anchor=W, bg='white', relief=RIDGE).grid(row=5, column=1, sticky=E+W+N+S)
        Label(self.help_train, text="Train-Test split", bg='yellow', padx=10, relief=RIDGE).grid(row=6, column=0, sticky=E + W + N + S)
        Label(self.help_train, text="Percentage of dataset used for training, it must be a float between 0 and 1", anchor=W, bg='white', relief=RIDGE).grid(row=6, column=1, sticky=E + W + N + S)
        Label(self.help_train, text="Epochs", bg='yellow', padx=10, relief=RIDGE).grid(row=7, column=0, sticky=E + W + N + S)
        Label(self.help_train, text="Number of epochs for training, it must be an integer", anchor=W, bg='white', relief=RIDGE).grid(row=7, column=1, sticky=E + W + N + S)
        Label(self.help_train, text="Batch size", bg='yellow', padx=10, relief=RIDGE).grid(row=8, column=0, sticky=E + W + N + S)
        Label(self.help_train, text="Number of samples used at one optimization, it must be an integer", anchor=W, bg='white', relief=RIDGE).grid(row=8, column=1, sticky=E + W + N + S)
        Label(self.help_train, text="Validation split", bg='yellow', padx=10, relief=RIDGE).grid(row=9, column=0, sticky=E + W + N + S)
        Label(self.help_train, text="Percentage of training dataset used for validation, it must be a float between 0 and 1", anchor=W, bg='white', relief=RIDGE).grid(row=9, column=1, sticky=E + W + N + S)
        Label(self.help_train, text="Patience", bg='yellow', padx=10, relief=RIDGE).grid(row=10, column=0, sticky=E + W + N + S)
        Label(self.help_train, text="Number of failures for early stopping, it must be an integer", anchor=W, bg='white', relief=RIDGE).grid(row=10, column=1, sticky=E + W + N + S)
        Label(self.help_train, text="Excel spreadsheet must look like the image below", bg='yellow', padx=10, relief=RIDGE).grid(row=0, column=2, sticky=E + W + N + S)
        self.deathwing = Image.open('dataset_spreasheet.png')
        self.image2 = self.deathwing.resize((320, 210), Image.ANTIALIAS)
        self.Deathwing0 = ImageTk.PhotoImage(self.image2)
        Label(self.help_train, image=self.Deathwing0).grid(row=1, column=2, rowspan=10, sticky=E+W+N+S)
    def train_results(self):
        self.top_train_results = Toplevel()
        self.top_train_results.geometry('+%d+%d'%(0,0))
        self.deathwing = Image.open('logolcap.png')
        self.image2 = self.deathwing.resize((320, 210), Image.ANTIALIAS)
        self.Deathwing1 = ImageTk.PhotoImage(self.image2)
        Label(self.top_train_results, text="Train", bg='grey', padx=7).grid(row=1, column=0, sticky=E+W+N+S)
        Label(self.top_train_results, text="Test", bg='grey', padx=7).grid(row=2, column=0, sticky=E + W + N + S)
        Label(self.top_train_results, text="Offline", bg='grey', padx=7).grid(row=3, column=0, sticky=E + W + N + S)
        Label(self.top_train_results, image=self.Deathwing1).grid(row=0, column=0, columnspan=6, sticky=E + W + N + S)
        self.tr_v = Button(self.top_train_results, text='V', bg='white', padx=5, relief=RIDGE, command=self.click_tr_v)
        self.te_v = Button(self.top_train_results, text='V', bg='white', padx=5, relief=RIDGE, command=self.click_te_v)
        self.tr_x = Button(self.top_train_results, text='X', bg='white', padx=5, relief=RIDGE, command=self.click_tr_x)
        self.te_x = Button(self.top_train_results, text='X', bg='white', padx=5, relief=RIDGE, command=self.click_te_x)
        self.tr_p = Button(self.top_train_results, text='P', bg='white', padx=5, relief=RIDGE, command=self.click_tr_p)
        self.te_p = Button(self.top_train_results, text='P', bg='white', padx=5, relief=RIDGE, command=self.click_te_p)
        self.tr_s = Button(self.top_train_results, text='S', bg='white', padx=5, relief=RIDGE, command=self.click_tr_s)
        self.te_s = Button(self.top_train_results, text='S', bg='white', padx=5, relief=RIDGE, command=self.click_te_s)
        self.off_v = Button(self.top_train_results, text='V', bg='white', padx=5, relief=RIDGE, command=self.click_off_v)
        self.off_x = Button(self.top_train_results, text='X', bg='white', padx=5, relief=RIDGE, command=self.click_off_x)
        self.off_p = Button(self.top_train_results, text='P', bg='white', padx=5, relief=RIDGE, command=self.click_off_p)
        self.off_s = Button(self.top_train_results, text='S', bg='white', padx=5, relief=RIDGE, command=self.click_off_s)

        self.tr_v.grid(row=1, column=1, sticky=E + W + N + S)
        self.te_v.grid(row=2, column=1, sticky=E + W + N + S)
        self.off_v.grid(row=3, column=1, sticky=E + W + N + S)
        self.tr_x.grid(row=1, column=2, sticky=E + W + N + S)
        self.te_x.grid(row=2, column=2, sticky=E + W + N + S)
        self.off_x.grid(row=3, column=2, sticky=E + W + N + S)
        self.tr_p.grid(row=1, column=3, sticky=E + W + N + S)
        self.te_p.grid(row=2, column=3, sticky=E + W + N + S)
        self.off_p.grid(row=3, column=3, sticky=E + W + N + S)
        self.tr_s.grid(row=1, column=4, sticky=E + W + N + S)
        self.te_s.grid(row=2, column=4, sticky=E + W + N + S)
        self.off_s.grid(row=3, column=4, sticky=E + W + N + S)

        self.cost = Button(self.top_train_results, text='Cost', bg='white', padx=10, relief=RIDGE)
        self.cost.configure(command=self.click_cost)
        self.cost.grid(row=1, column=5, sticky=E+W+N+S)
        self.save_train = Button(self.top_train_results, text="Save Images", bg='white', padx=10, relief=RIDGE)
        self.save_train.configure(command=self.click_save_train)
        self.save_train.grid(row=2, column=5, sticky=E+W+N+S, rowspan=2)
        self.tempo_treino = np.linspace(0, int(len(self.y_train)*3-3), int(len(self.y_train)))
        self.tempo_test = np.linspace(0, int(len(self.y_test) * 3-3), int(len(self.y_test)))
        self.tempo_off = np.linspace(0, int(len(self.y_real) * 3-3), int(len(self.y_real)))
    def click_tr_v(self):
        if self.tr_v['bg'] == 'white':
            self.tr_v['bg'] = 'blue'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('V (L)')
            plt.plot(self.tempo_treino, self.y_train[:,0], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_treino, self.train_predict[:,0], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    def click_tr_x(self):
        if self.tr_x['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'blue'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('X (g/L)')
            plt.plot(self.tempo_treino, self.y_train[:,1], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_treino, self.train_predict[:,1], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    def click_tr_s(self):
        if self.tr_s['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'blue'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('S (g/L)')
            plt.plot(self.tempo_treino, self.y_train[:,2], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_treino, self.train_predict[:,2], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    def click_tr_p(self):
        if self.tr_p['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'blue'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('P (g/L)')
            plt.plot(self.tempo_treino, self.y_train[:,3], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_treino, self.train_predict[:,3], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    def click_te_v(self):
        if self.te_v['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'blue'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('V (L)')
            plt.plot(self.tempo_test, self.y_test[:,0], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_test, self.test_predict[:,0], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    def click_te_x(self):
        if self.te_x['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'blue'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('X (g/L)')
            plt.plot(self.tempo_test, self.y_test[:, 1], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_test, self.test_predict[:, 1], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    def click_te_s(self):
        if self.te_s['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'blue'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('S (g/L)')
            plt.plot(self.tempo_test, self.y_test[:, 2], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_test, self.test_predict[:, 2], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    def click_te_p(self):
        if self.te_p['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'blue'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('P (g/L)')
            plt.plot(self.tempo_test, self.y_test[:, 3], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_test, self.test_predict[:, 3], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()
    def click_cost(self):
        if self.cost['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'blue'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.plot(self.history.history['loss'], color='red')
            plt.plot(self.history.history['val_loss'], color='blue')
            plt.ylabel('Cost Function (MSE)')
            plt.xlabel('Epoch')
            plt.legend(['Train set', 'Validation set'], loc='upper right')
            plt.grid('True')
            plt.tight_layout()
            plt.show()
    def click_off_v(self):
        if self.off_v['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'blue'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('V (L)')
            plt.plot(self.tempo_off, self.y_real[:, 0], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_off, self.y_offline[:, 0], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    def click_off_x(self):
        if self.off_x['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'blue'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('X (g/L)')
            plt.plot(self.tempo_off, self.y_real[:, 1], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_off, self.y_offline[:, 1], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    def click_off_p(self):
        if self.off_p['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'blue'
            self.off_s['bg'] = 'white'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('P (g/L)')
            plt.plot(self.tempo_off, self.y_real[:, 3], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_off, self.y_offline[:, 3], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()
    def click_off_s(self):
        if self.off_s['bg'] == 'white':
            self.tr_v['bg'] = 'white'
            self.tr_x['bg'] = 'white'
            self.tr_s['bg'] = 'white'
            self.tr_p['bg'] = 'white'
            self.te_v['bg'] = 'white'
            self.te_x['bg'] = 'white'
            self.te_s['bg'] = 'white'
            self.te_p['bg'] = 'white'
            self.cost['bg'] = 'white'
            self.off_v['bg'] = 'white'
            self.off_x['bg'] = 'white'
            self.off_p['bg'] = 'white'
            self.off_s['bg'] = 'blue'
            plt.close()
            plt.figure()
            plt.xlabel('Time (h)')
            plt.ylabel('S (g/L)')
            plt.plot(self.tempo_off, self.y_real[:, 2], color='blue', label='Real', linewidth=2)
            plt.plot(self.tempo_off, self.y_offline[:, 2], color='red', label='Prediction', linewidth=2)
            plt.grid('True')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()
    def click_save_train(self):
        directory = filedialog.askdirectory(title="Select the directory to save the images", initialdir=os.getcwd())
        self.directory_tr_v = str(directory + '/train_V.png')
        self.directory_tr_x = str(directory + '/train_X.png')
        self.directory_tr_s = str(directory + '/train_S.png')
        self.directory_tr_p = str(directory + '/train_P.png')
        self.directory_te_v = str(directory + '/test_V.png')
        self.directory_te_x = str(directory + '/test_X.png')
        self.directory_te_s = str(directory + '/test_S.png')
        self.directory_te_p = str(directory + '/test_P.png')
        self.directory_cost = str(directory + '/cost.png')
        self.directory_off_v = str(directory + '/offline_V.png')
        self.directory_off_x = str(directory + '/offline_X.png')
        self.directory_off_s = str(directory + '/offline_S.png')
        self.directory_off_p = str(directory + '/offline_P.png')
        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('V (L)')
        plt.plot(self.tempo_treino, self.y_train[:, 0], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_treino, self.train_predict[:, 0], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory_tr_v, dpi=600)

        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('X (g/L)')
        plt.plot(self.tempo_treino, self.y_train[:, 1], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_treino, self.train_predict[:, 1], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory_tr_x, dpi=600)

        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('S (g/L)')
        plt.plot(self.tempo_treino, self.y_train[:, 2], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_treino, self.train_predict[:, 2], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory_tr_s, dpi=600)

        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('P (g/L)')
        plt.plot(self.tempo_treino, self.y_train[:, 3], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_treino, self.train_predict[:, 3], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory_tr_p, dpi=600)

        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('V (L)')
        plt.plot(self.tempo_test, self.y_test[:, 0], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_test, self.test_predict[:, 0], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory_te_v, dpi=600)

        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('X (g/L)')
        plt.plot(self.tempo_test, self.y_test[:, 1], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_test, self.test_predict[:, 1], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory_te_x, dpi=600)

        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('S (g/L)')
        plt.plot(self.tempo_test, self.y_test[:, 2], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_test, self.test_predict[:, 2], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory_te_s, dpi=600)

        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('P (g/L)')
        plt.plot(self.tempo_test, self.y_test[:, 3], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_test, self.test_predict[:, 3], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory_te_p, dpi=600)

        plt.close()
        plt.figure()
        plt.plot(self.history.history['loss'], color='red')
        plt.plot(self.history.history['val_loss'], color='blue')
        plt.ylabel('Cost Function (MSE)')
        plt.xlabel('Epoch')
        plt.legend(['Train set', 'Validation set'], loc='upper right')
        plt.grid('True')
        plt.tight_layout()
        plt.savefig(self.directory_cost, dpi=600)

        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('V (L)')
        plt.plot(self.tempo_off, self.y_real[:, 0], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_off, self.y_offline[:, 0], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.savefig(self.directory_off_v, dpi=600)

        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('X (g/L)')
        plt.plot(self.tempo_off, self.y_real[:, 1], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_off, self.y_offline[:, 1], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.savefig(self.directory_off_x, dpi=600)

        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('P (g/L)')
        plt.plot(self.tempo_off, self.y_real[:, 3], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_off, self.y_offline[:, 3], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.savefig(self.directory_off_p, dpi=600)

        plt.close()
        plt.figure()
        plt.xlabel('Time (h)')
        plt.ylabel('S (g/L)')
        plt.plot(self.tempo_off, self.y_real[:, 2], color='blue', label='Real', linewidth=2)
        plt.plot(self.tempo_off, self.y_offline[:, 2], color='red', label='Prediction', linewidth=2)
        plt.grid('True')
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.savefig(self.directory_off_s, dpi=600)

        self.tr_v['bg'] = 'white'
        self.tr_x['bg'] = 'white'
        self.tr_s['bg'] = 'white'
        self.tr_p['bg'] = 'white'
        self.te_v['bg'] = 'white'
        self.te_x['bg'] = 'white'
        self.te_s['bg'] = 'white'
        self.te_p['bg'] = 'white'
        self.cost['bg'] = 'white'
        self.off_v['bg'] = 'white'
        self.off_x['bg'] = 'white'
        self.off_p['bg'] = 'white'
        self.off_s['bg'] = 'white'

myapp = MyApp(root)
root.mainloop()
