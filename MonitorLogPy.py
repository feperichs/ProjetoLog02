import random
import datetime

def menu():
    nome_arq = "log.txt"
    while True:
        print("MENU\n")
        print("1 - Gerar logs")
        print("2 - Analisar logs")
        print("3 - Gerar e Analisar logs")
        print("4 - Sair")
        opc = int(input("Escolha uma opção: "))
        if opc == 1:
            try:
                qtd = int(input("Quantidade de logs (registros): "))
                gerarArquivo(nome_arq, qtd)
            except:
                print("Entrada inválida.")
        elif opc == 2:
            analisarLogs(nome_arq)
        elif opc == 3:
            try:
                qtd = int(input("Quantidade de logs (registros): "))
                gerarArquivo(nome_arq, qtd)
                analisarLogs(nome_arq)
            except:
                print("Entrada inválida.")
        elif opc == 4:
            print("Até mais")
            break
        else:
            print("Opção inváçida")

def gerarArquivo(nome_arq, qtd):
    with open(nome_arq, "w", encoding="UTF-8") as arq:
        for i in range(qtd):    
            arq.write(montarLog(i) + "\n")
        print ("Log gerado")

def montarLog(i):
    data = gerarData(i)
    ip = gerarIp(i)
    recurso = gerarRecurso(i)
    metodo = gerarMetodo(i)
    status = gerarStatus(i)
    tempo = gerarTempo(i)
    agente = gerarAgente(i)
    protocolo = gerarProtocolo(i)
    tamanho = gerarTamanho(i)
    return f"[{data}] {i} - {metodo} - {status} - {recurso} - {tempo}ms {tamanho} - {protocolo} - {agente} - /home"

def gerarData(i):
    base = datetime.datetime.now()
    delta =datetime.delta(seconds= i * random.randint(5,20) )
    return (base +delta).strftime("%d/%m/%Y %H:%M:%S")

def gerarIp(i)
    r = random.randint(1,6)
    if i >= 20 and i <= 50:
        return "203.120.45.7"
    else:
        return f"{random.randit(10,200).{random.randint(100,200)}.{random.randint(0,250)}}.{random.randint(1,250)}"
    