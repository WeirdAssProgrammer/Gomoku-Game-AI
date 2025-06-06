# src/gui.py
from concurrent.futures import ThreadPoolExecutor
import random
import threading
import time
tk = __import__('tkinter')
from os import _exit as exit_os
from tkinter import messagebox
from PIL import Image, ImageTk
from src.game import Game
from src.ai import AlphaBetaAI, MinimaxAI

BOARD_SIZE=15; ICON=40

def start_gui():
    global root
    root = tk.Tk()
    root.title("Gomoku")
    root.geometry("800x600")
    root.resizable(False,False)
    bg=ImageTk.PhotoImage(Image.open("assets/image.png").resize((800,600)))
    cv=tk.Canvas(root,width=800,height=600)
    cv.pack()
    cv.create_image(0,0,image=bg,anchor="nw")
    cv.create_text(400,100,text="Gomoku Game",font=("Helvetica",36,"bold"),fill="white")
    b1=tk.Button(root,text="Human vs AI",font=(None,16),width=20,command=start_human_vs_ai)
    b2=tk.Button(root,text="AI vs AI",font=(None,16),width=20,command=start_ai_vs_ai)
    b3=tk.Button(root,text="Quit",font=(None,16),width=20,command=lambda:(messagebox.showinfo("Bye","Cya"),exit_os(0)))
    cv.create_window(400,250,window=b1); cv.create_window(400,320,window=b2)
    cv.create_window(400,400,window=b3)
    root.mainloop()

# Human vs AI

def start_human_vs_ai():
    """ 
    Human vs Ai mode:
        15x15 grid, Alpha beta ai vs human input
        background img humanvsai.jpeg, allow user to choose a side black or white, optmize speed and utlize the Game class to detect winner and invalid positions and other gomoku rules
    """
    # init window, add title, draw grid, and prompt for the player color
    root.withdraw()

    # Classes
    game=Game(BOARD_SIZE)
    ai=AlphaBetaAI(2)
    # Draw Window with title and button grid, ask user for role
    w=tk.Toplevel()
    w.title("Human vs AI")
    w.geometry("800x600")
    w.resizable(False,False)
    choice=messagebox.askquestion("Color","Play as Black? Yes/No")
    human='B' if choice=='yes' else 'W'
    human_img=ImageTk.PhotoImage(Image.open(f"assets/{'black' if human=='B' else 'white'}.jpeg").resize((ICON,ICON)))
    ai_p=('W' if human=='B' else 'B')
    ai_img=ImageTk.PhotoImage(Image.open(f"assets/{'black' if ai_p=='B' else 'white'}.jpeg").resize((ICON,ICON)))
    bg=ImageTk.PhotoImage(Image.open("assets/humanvsai.jpeg").resize((800,600)))
    lbl=tk.Label(w,image=bg)
    lbl.image=bg; lbl.place(x=0,y=0,relwidth=1,relheight=1)
    tk.Label(w,text="Human vs AI Mode",font=("Helvetica",24,"bold"),fg="white",bg="black").place(relx=0.5,rely=0.05,anchor="center")
    frm=tk.Frame(w,bg="black")
    frm.place(relx=0.5,rely=0.55,anchor="center")
    btns={}
    def human_move(x,y):
        """ Record human move as (X,Y) and send for the game object, update grid often to show the Ai move """
        if game.is_game_over(): return
        try:
            game.place_stone(x,y)
            btns[(x,y)].config(image=human_img, width=20, height=20); btns[(x,y)].image=human_img
            print("Human",(x,y))
        except Exception as e:
            return messagebox.showwarning("Bad Move",str(e))
        if game.is_game_over(): messagebox.showinfo("Game Over","Human wins!"); return
        # run AI in thread
        threading.Thread(target=ai_turn,daemon=True).start()

    def ai_turn():
        """ Allow Ai to make a move, record it to the grid and print the Ai move """
        mv=ai.get_move(game)
        if not mv: return
        game.place_stone(*mv)
        btns[mv].config(image=ai_img, width=20, height=20); btns[mv].image=ai_img
        print("AI",mv)
        if game.is_game_over(): messagebox.showinfo("Game Over","AI wins!")
    # init grid
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            b=tk.Button(frm,width=2,height=1,command=lambda x=i,y=j: human_move(x,y))
            b.grid(row=i,column=j,padx=2,pady=2)
            btns[(i,j)]=b
    tk.Button(w,text="Quit to Menu",font=(None,14),command=lambda:(w.destroy(),root.deiconify())).place(relx=0.5,rely=0.9,anchor="center")
    w.mainloop()

# AI vs AI stub
# TODO: Create logic for Ai vs Ai
# --- AI vs AI ---
def start_ai_vs_ai():
    root.withdraw()
    game = Game(BOARD_SIZE)
    ai1 = AlphaBetaAI(2)
    ai2 = MinimaxAI(2)

    # Preload piece images
    black_icon = ImageTk.PhotoImage(
        Image.open("assets/black.jpeg").resize((ICON,ICON))
    )
    white_icon = ImageTk.PhotoImage(
        Image.open("assets/white.jpeg").resize((ICON,ICON))
    )

    w = tk.Toplevel()
    w.title("AI vs AI")
    w.geometry("800x600")
    w.resizable(False, False)

    bg = ImageTk.PhotoImage(Image.open("assets/aivsai.jpg").resize((800,600)))
    lbl = tk.Label(w, image=bg); lbl.image=bg; lbl.place(x=0,y=0,relwidth=1,relheight=1)
    tk.Label(w, text="AI vs AI Mode", font=("Helvetica",24,"bold"), fg="white", bg="black").place(relx=0.5, rely=0.05, anchor="center")

    frm = tk.Frame(w, bg="black")
    frm.place(relx=0.5, rely=0.55, anchor="center")
    lbls = {}

    # draw empty board
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            l = tk.Label(frm, width=2, height=1, bg="lightgrey", relief="solid")
            l.grid(row=i, column=j, padx=0, pady=0)
            lbls[(i,j)] = l

    def play_turn():
        if game.is_game_over():
            winner = game.get_winner()
            msg = "AlphaBeta wins!" if winner=='B' else "Minimax wins!"
            messagebox.showinfo("Game Over", msg)
            return
        current = game.active_player
        ai = ai1 if current=='B' else ai2
        mv = ai.get_move(game)
        if mv:
            game.place_stone(*mv)
            img = black_icon if current=='B' else white_icon
            lbls[mv].config(image=img, width=16, height=16)
            lbls[mv].image = img
        # schedule next turn without blocking
        w.after(100, play_turn)

    # start immediately
    w.after(100, play_turn)

    tk.Button(w, text="Quit to Menu", font=(None,14), command=lambda: (w.destroy(), root.deiconify())).place(relx=0.5, rely=0.9, anchor="center")
    w.mainloop()

if __name__=='__main__': start_gui()
