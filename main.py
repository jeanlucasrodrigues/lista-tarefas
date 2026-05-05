import customtkinter
import sqlite3

#Fazendo a conexão com o banco de dados
conexao = sqlite3.connect("tarefas.db")
cursor = conexao.cursor()

# Criando a tabela
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        concluida INTEGER DEFAULT 0
    )
""")
conexao.commit()


app = customtkinter.CTk()
app.geometry("700x500")
app.title("Lista de Tarefas")

customtkinter.set_appearance_mode('Dark')

lista_de_tarefas =[]
#Vou salvar as tarefas aqui

def carregar_tarefas_do_banco():
    # Limpa a tela
    for item in lista_de_tarefas:
        item.destroy()
    lista_de_tarefas.clear()

    # Busca no Banco
    cursor.execute("SELECT * FROM tarefas")
    dados = cursor.fetchall()

    # Na parte de cima ele repopula a tabela com os dados do banco
    # Aqui na parte de baixo, para cada dado, ele vai criar uma checkbox e adicionar na tabela
    for linha in dados:
        # linha[1] é o nome, linha[2] é o status 'concluida'
        texto_tarefa = linha[1]
        status_concluido = linha[2]
        if status_concluido == 1:
            nova_tarefa = customtkinter.CTkCheckBox(
                master=frame_lista, 
                text=texto_tarefa, 
                font=("Roboto", 16, "overstrike"), 
                text_color="gray"
            )
        else:
            nova_tarefa = customtkinter.CTkCheckBox(
                master=frame_lista, 
                text=texto_tarefa
            )
            
        nova_tarefa.pack(pady=5, anchor="w", padx=10)
        lista_de_tarefas.append(nova_tarefa)


def fechar_programa():
    conexao.close() #Fechando o banco de dados ao sair do programa
    app.destroy()  

def abrir_aviso_customizado():
    janela_aviso = customtkinter.CTkToplevel(app)
    janela_aviso.geometry("300x150")
    janela_aviso.title("Aviso Importante")
    
    # Fazendo a janela aparecer em cima de tudo
    janela_aviso.attributes("-topmost", True)


    label = customtkinter.CTkLabel(janela_aviso, text="Coloque um texto para inserir", pady=20)
    label.pack()
    janela_aviso.grab_set() #Impedindo que o usuario utilize o programa ate fechar o aviso
    btn_fechar = customtkinter.CTkButton(janela_aviso, text="Ok", command=janela_aviso.destroy)
    btn_fechar.pack(pady=10)

def aviso_are_you_sure(acao):

    janela_aviso = customtkinter.CTkToplevel(app)
    janela_aviso.geometry("300x150")
    janela_aviso.title("Cuidado")

    janela_aviso.attributes("-topmost",True)
    janela_aviso.grab_set()

    #Ele executa a ação caso o botão seja sim, assim utilizo apenas uma janela de aviso
    def botao_sim():
        acao()
        janela_aviso.destroy()

    
    texto = customtkinter.CTkLabel(janela_aviso, text='Essa ação é irreversivel, deseja continuar?',pady=20)
    texto.pack()

    btn_sim = customtkinter.CTkButton(janela_aviso, text="Sim", command=botao_sim)
    btn_sim.pack(pady=5)

    btn_nao = customtkinter.CTkButton(janela_aviso,text="Não", command=janela_aviso.destroy)
    btn_nao.pack(pady=5)

def adicionar_tarefa():
    texto = entrada.get() #Pega o texto da entrada
    if texto != "":
        cursor.execute("INSERT INTO tarefas (nome) VALUES (?)", (texto,))
        conexao.commit()
        
        entrada.delete(0, "end") #Deleta do primeiro caracter (0) até o ultimo ("end")
        carregar_tarefas_do_banco() 
    else:
        abrir_aviso_customizado()

def remover_tarefa():
    for check in lista_de_tarefas[:]: #O [:] aqui é para faer o for em uma copia da lista
        if check.get() == 1:
            texto = check.cget("text")
            
            #Deletando pelo texto das checkboxs marcas ( == 1)
            cursor.execute("DELETE FROM tarefas WHERE nome = ?", (texto,)) 
            conexao.commit()
            
    
    carregar_tarefas_do_banco()

def alterar_tarefa():
    texto = entrada.get()
    for check in lista_de_tarefas:
        if check.get() == 1:
            check.configure(text=texto) 
            
            
            check.deselect() #Desmarcando a caixa
            entrada.delete(0, "end")
            break

def coloca_concluido():
    for check in lista_de_tarefas:
        if check.get() == 1:
            nome_tarefa = check.cget("text") #Aqui ele percorre todos os checks e só pega o texto do marcado
            check.configure(font=(("Roboto", 14, "overstrike"))) 
    #colocando sublinhado em tarefas concluidas
            cursor.execute("UPDATE tarefas SET concluida = 1 where nome = ?",(nome_tarefa,))
            conexao.commit()
            check.deselect()

app.grid_columnconfigure(1, weight=1) # O Weight1 é para ele ocupar o espaço da janela
app.grid_rowconfigure(0, weight=1) 

#MENU
frame_menu = customtkinter.CTkFrame(master=app, width=150, corner_radius=0, border_width=2)
frame_menu.grid(row=0, column=0, sticky="nsew") 
#O botão de baixo, o master vai ser o frame-menu, então eu vou colocando o pack e ele vai adicionando na ordem desejada
adicionar_botao = customtkinter.CTkButton(frame_menu, text='Inserir', command=adicionar_tarefa, fg_color="#5454A7",
            hover_color="#4317F0", border_color="#ffffff", border_width=2)
adicionar_botao.pack(pady=10, padx=10)
#O Botão lambda, faz a função só executar, quando o botão for clicado, pois eu estou passando o comando por parenteses e por padrão, o Python executa as funções assim que o código é executado
remover_botao = customtkinter.CTkButton(frame_menu, command=lambda: aviso_are_you_sure(remover_tarefa), text='Deletar', fg_color="#5454A7",
            hover_color="#4317F0", border_color="#ffffff", border_width=2)
remover_botao.pack(pady=10, padx=10)

alterar_botao = customtkinter.CTkButton(frame_menu, command=lambda: aviso_are_you_sure(alterar_tarefa), text='Alterar', fg_color="#5454A7",
            hover_color="#4317F0", border_color="#ffffff",border_width=2)
alterar_botao.pack(pady=10, padx=10)


#CONTEUDO
frame_direita = customtkinter.CTkFrame(master=app, fg_color="transparent")
frame_direita.grid(row=0, column=1, sticky="nsew", padx=20)


label_titulo = customtkinter.CTkLabel(frame_direita, text="Tarefas a fazer", font=("Roboto", 24, "bold"))
label_titulo.pack(pady=20, anchor="w")


entrada = customtkinter.CTkEntry(frame_direita, placeholder_text='Insira a tarefa', width=300)
entrada.pack(pady=10, anchor="w")

# Botão Marcar concluido
botao_extra = customtkinter.CTkButton(frame_direita, text="Marcar concluido", command=coloca_concluido)
botao_extra.pack(pady=10, anchor="w")

#lista de tarefas
frame_lista = customtkinter.CTkScrollableFrame(frame_direita, label_text="Tarefas Pendentes")
frame_lista.pack(pady=10, fill="both", expand=True) #

creditos = customtkinter.CTkLabel(frame_direita, text='Feito por Jean')
creditos.pack (side='bottom')

carregar_tarefas_do_banco()
app.protocol("WM_DELETE_WINDOW", fechar_programa) #Aqui ele esta fechando o banco de dados ao clicar no x
app.mainloop()