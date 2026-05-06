import customtkinter
import sqlite3

class AppTarefas(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- Configurações Iniciais ---
        self.geometry("700x500")
        self.title("Lista de Tarefas")
        customtkinter.set_appearance_mode('Dark')

        # Fazendo a conexão com o banco de dados
        self.conexao = sqlite3.connect("tarefas.db")
        self.cursor = self.conexao.cursor()

        # Criando a tabela
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                concluida INTEGER DEFAULT 0
            )
        """)
        self.conexao.commit()

        # Vou salvar as tarefas aqui
        self.lista_de_tarefas = []

        # Configuração do Grid do App
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # Montar a Interface
        self.criar_layout()
        self.carregar_tarefas_do_banco()
        
        # Aqui ele esta fechando o banco de dados ao clicar no x
        self.protocol("WM_DELETE_WINDOW", self.fechar_programa)

    def criar_layout(self):
        # --- MENU ---
        self.frame_menu = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, border_width=2)
        self.frame_menu.grid(row=0, column=0, sticky="nsew") 

        self.adicionar_botao = customtkinter.CTkButton(self.frame_menu, text='Inserir', command=self.adicionar_tarefa, 
                                                       fg_color="#5454A7", hover_color="#4317F0", border_color="#ffffff", border_width=2)
        self.adicionar_botao.pack(pady=10, padx=10)

        self.remover_botao = customtkinter.CTkButton(self.frame_menu, command=lambda: self.aviso_are_you_sure(self.remover_tarefa), 
                                                     text='Deletar', fg_color="#5454A7", hover_color="#4317F0", border_color="#ffffff", border_width=2)
        self.remover_botao.pack(pady=10, padx=10)

        self.alterar_botao = customtkinter.CTkButton(self.frame_menu, command=lambda: self.aviso_are_you_sure(self.alterar_tarefa), 
                                                     text='Alterar', fg_color="#5454A7", hover_color="#4317F0", border_color="#ffffff", border_width=2)
        self.alterar_botao.pack(pady=10, padx=10)

        # --- CONTEUDO ---
        self.frame_direita = customtkinter.CTkFrame(master=self, fg_color="transparent")
        self.frame_direita.grid(row=0, column=1, sticky="nsew", padx=20)

        self.label_titulo = customtkinter.CTkLabel(self.frame_direita, text="Tarefas a fazer", font=("Roboto", 24, "bold"))
        self.label_titulo.pack(pady=20, anchor="w")

        self.entrada = customtkinter.CTkEntry(self.frame_direita, placeholder_text='Insira a tarefa', width=300)
        self.entrada.pack(pady=10, anchor="w")

        self.botao_extra = customtkinter.CTkButton(self.frame_direita, text="Marcar concluido", command=self.coloca_concluido)
        self.botao_extra.pack(pady=10, anchor="w")

        self.frame_lista = customtkinter.CTkScrollableFrame(self.frame_direita, label_text="Tarefas Pendentes")
        self.frame_lista.pack(pady=10, fill="both", expand=True)

        self.creditos = customtkinter.CTkLabel(self.frame_direita, text='Feito por Jean')
        self.creditos.pack(side='bottom')

    # --- MÉTODOS DE LÓGICA (Mantendo seus comentários) ---

    def carregar_tarefas_do_banco(self):
        for item in self.lista_de_tarefas:
            item.destroy()
        self.lista_de_tarefas.clear()

        self.cursor.execute("SELECT * FROM tarefas")
        dados = self.cursor.fetchall()

        for linha in dados:
            texto_tarefa = linha[1]
            status_concluido = linha[2]
            
            if status_concluido == 1:
                nova_tarefa = customtkinter.CTkCheckBox(master=self.frame_lista, text=texto_tarefa, 
                                                       font=("Roboto", 16, "overstrike"), text_color="gray")
            else:
                nova_tarefa = customtkinter.CTkCheckBox(master=self.frame_lista, text=texto_tarefa)
                
            nova_tarefa.pack(pady=5, anchor="w", padx=10)
            self.lista_de_tarefas.append(nova_tarefa)

    def fechar_programa(self):
        self.conexao.close() 
        self.destroy()  

    def abrir_aviso_customizado(self):
        janela_aviso = customtkinter.CTkToplevel(self)
        janela_aviso.geometry("300x150")
        janela_aviso.title("Aviso Importante")
        janela_aviso.attributes("-topmost", True)
        janela_aviso.grab_set() 
        btn_fechar = customtkinter.CTkButton(janela_aviso, text="Ok", command=janela_aviso.destroy)
        btn_fechar.pack(pady=10)

    def aviso_are_you_sure(self, acao):
        janela_aviso = customtkinter.CTkToplevel(self)
        janela_aviso.geometry("300x150")
        janela_aviso.title("Cuidado")
        janela_aviso.attributes("-topmost", True)
        janela_aviso.grab_set()

        def botao_sim():
            acao()
            janela_aviso.destroy()

        texto = customtkinter.CTkLabel(janela_aviso, text='Essa ação é irreversivel, deseja continuar?', pady=20)
        texto.pack()
        customtkinter.CTkButton(janela_aviso, text="Sim", command=botao_sim).pack(pady=5)
        customtkinter.CTkButton(janela_aviso, text="Não", command=janela_aviso.destroy).pack(pady=5)

    def adicionar_tarefa(self):
        texto = self.entrada.get()
        if texto != "":
            self.cursor.execute("INSERT INTO tarefas (nome) VALUES (?)", (texto,))
            self.conexao.commit()
            self.entrada.delete(0, "end")
            self.carregar_tarefas_do_banco() 
        else:
            self.abrir_aviso_customizado()

    def remover_tarefa(self):
        for check in self.lista_de_tarefas[:]:
            if check.get() == 1:
                texto = check.cget("text")
                self.cursor.execute("DELETE FROM tarefas WHERE nome = ?", (texto,)) 
                self.conexao.commit()
        self.carregar_tarefas_do_banco()

    def alterar_tarefa(self):
        texto = self.entrada.get()
        for check in self.lista_de_tarefas:
            if check.get() == 1:
                check.configure(text=texto) 
                check.deselect() 
                self.entrada.delete(0, "end")
                break

    def coloca_concluido(self):
        for check in self.lista_de_tarefas:
            if check.get() == 1:
                nome_tarefa = check.cget("text")
                check.configure(font=("Roboto", 16, "overstrike"), text_color="gray") 
                self.cursor.execute("UPDATE tarefas SET concluida = 1 WHERE nome = ?", (nome_tarefa,))
                self.conexao.commit()
                check.deselect()