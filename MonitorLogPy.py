import random
import datetime

# GERAÇÃO DO ARQUIVO DE LOGS

def gerarData(i):
    base = datetime.datetime.now()
    delta = datetime.timedelta(seconds=i * random.randint(5, 20))
    return (base + delta).strftime("%d/%m/%Y %H:%M:%S")

def gerar_ip(indice):
    # IPs fixos para gatilhos de segurança
    if 100 <= indice <= 105: return "10.0.0.5"    # Suspeita de Bot
    if 200 <= indice <= 203: return "172.16.0.1" # Força Bruta
    # IP aleatório controlado
    return f"189.20.{indice % 255}.{random.randint(1, 254)}"

def gerar_recurso(indice):
    if 200 <= indice <= 203: return "/login"
    rotas = ["/home", "/admin", "/produtos", "/contato", "/config", "/busca", "/perfil", "/carrinho"]
    pesos = [18, 10, 16, 14, 10, 12, 10, 10]
    return random.choices(rotas, weights=pesos, k=1)[0]

def gerar_status(indice, recurso):
    # Força Bruta
    if 200 <= indice <= 203 and recurso == "/login": return "403"
    # Falha Crítica (3 erros 500 seguidos)
    if 400 <= indice <= 402: return "500"
    # Aleatoriedade geral com alguns 404 naturais
    if recurso in ["/busca", "/perfil", "/carrinho"] and random.randint(1, 10) <= 2:
        return "404"
    # Acesso negado em áreas sensíveis
    if recurso == "/admin" or recurso == "/config":
        return random.choices(["200", "403"], weights=[3, 7], k=1)[0]
    return random.choices(["200", "200", "200", "403", "404"], k=1)[0]

def gerar_tempo_resposta(indice, status, recurso):
    # Simulação de Degradação (aumento contínuo)
    if 300 <= indice <= 303:
        return 500 + (indice - 300) * 150
    base = {
        "/home": (80, 220),
        "/admin": (180, 900),
        "/produtos": (120, 420),
        "/contato": (60, 260),
        "/config": (250, 980),
        "/busca": (140, 700),
        "/perfil": (90, 360),
        "/carrinho": (110, 480),
        "/login": (220, 850),
    }.get(recurso, (50, 950))

    minimo, maximo = base
    if status == "500":
        minimo += 120
        maximo += 250
    elif status == "403":
        minimo += 40
        maximo += 180
    elif status == "404":
        minimo -= 20
        maximo -= 40
    return random.randint(max(30, minimo), max(minimo + 10, maximo))

def gerar_arquivo_logs(nome_arquivo, quantidade):
    with open(nome_arquivo, "w", encoding="UTF-8") as arq:
        for i in range(quantidade):
            ip = gerar_ip(i)
            recurso = gerar_recurso(i)
            status = gerar_status(i, recurso)
            data = gerarData(i)
            metodo = random.choice(["GET", "GET", "GET", "POST", "PUT"])
            if recurso == "/login":
                metodo = random.choice(["POST", "POST", "GET"])
            tempo = gerar_tempo_resposta(i, status, recurso)
            tamanho = random.randint(100, 5000)
            ua = random.choice([
                "GoogleBot/2.1",
                "Chrome/122.0",
                "Mozilla/5.0",
                "BingBot/1.0",
                "Safari/17.0",
                "CrawlerX/3.4"
            ]) if i % 15 == 0 else random.choice([
                "Chrome/122.0",
                "Mozilla/5.0",
                "Safari/17.0",
                "Edge/121.0"
            ])
            
            # Formato: [DATA] IP - METODO - STATUS - RECURSO - TEMPOms - TAMANHOB - PROTOCOLO - UA - REF
            linha = f"[{data}] {ip} - {metodo} - {status} - {recurso} - {tempo}ms - {tamanho}B - HTTP/1.1 - {ua} - /home\n"
            arq.write(linha)
    print(f"\n[SUCESSO] {quantidade} logs gerados em '{nome_arquivo}'.")

# ANÁLISE DO ARQUIVO (EXTRAÇÃO MANUAL)

def analisar_arquivo_logs(nome_arquivo):
    # Contadores
    total = 0
    sucessos = 0
    erros = 0
    erros_500 = 0
    soma_tempo = 0
    maior_t = 0
    menor_t = 999999
    
    # Classificação
    qtd_rapido = 0
    qtd_normal = 0
    qtd_lento = 0
    
    st_200 = 0
    st_403 = 0
    st_404 = 0
    st_500 = 0

    # Sequências
    fb_ip = ""; fb_cont = 0; fb_total = 0; fb_ultimo = "Nenhum"
    deg_cont = 0; deg_ultimo_t = -1; deg_total = 0
    fc_cont = 0; fc_total = 0
    bot_ip = ""; bot_cont = 0; bot_total = 0; bot_ultimo = "Nenhum"
    
    # Sensíveis
    sens_total = 0; sens_falhas = 0; admin_indevido = 0
    
    # Strings para IP/Recurso mais ativos
    ip_mais = ""; rec_mais = ""
    cont_ip = {}
    cont_rec = {}

    try:
        with open(nome_arquivo, "r", encoding="UTF-8") as arq:
            for linha in arq:
                if not linha.strip(): continue
                total += 1

                # EXTRAÇÃO CONFIÁVEL DOS CAMPOS
                conteudo = linha.strip()
                if "] " not in conteudo:
                    continue
                _, resto = conteudo.split("] ", 1)
                campos = resto.split(" - ")
                if len(campos) < 9:
                    continue

                c_ip = campos[0]
                c_status = campos[2]
                c_recurso = campos[3]
                c_tempo = campos[4]
                c_ua = campos[7]

                t_str = ""
                for car in c_tempo:
                    if car in "0123456789": t_str += car
                num_t = int(t_str) if t_str else 0

                cont_ip[c_ip] = cont_ip.get(c_ip, 0) + 1
                cont_rec[c_recurso] = cont_rec.get(c_recurso, 0) + 1

                # Métricas
                soma_tempo += num_t
                if num_t > maior_t: maior_t = num_t
                if num_t < menor_t: menor_t = num_t
                
                if num_t < 200: qtd_rapido += 1
                elif num_t < 800: qtd_normal += 1
                else: qtd_lento += 1

                if c_status == "200":
                    sucessos += 1; st_200 += 1
                else:
                    erros += 1
                    if c_status == "403": st_403 += 1
                    elif c_status == "404": st_404 += 1
                    elif c_status == "500": st_500 += 1; erros_500 += 1

                # Lógica de Sequências
                # Força Bruta
                if c_recurso == "/login" and c_status == "403":
                    if c_ip == fb_ip: fb_cont += 1
                    else: fb_ip = c_ip; fb_cont = 1
                    if fb_cont == 3: fb_total += 1; fb_ultimo = c_ip
                else: fb_cont = 0

                # Degradação
                if num_t > deg_ultimo_t:
                    deg_cont += 1
                    if deg_cont == 3: deg_total += 1
                else: deg_cont = 0
                deg_ultimo_t = num_t

                # Falha Crítica
                if c_status == "500":
                    fc_cont += 1
                    if fc_cont == 3: fc_total += 1
                else: fc_cont = 0

                # Bot
                bot_match = False
                for b_word in ["Bot", "Crawler", "Spider"]:
                    if b_word in c_ua: bot_match = True
                
                if c_ip == bot_ip: bot_cont += 1
                else: bot_ip = c_ip; bot_cont = 1
                
                if bot_match or bot_cont == 5:
                    bot_total += 1; bot_ultimo = c_ip

                # Rotas Sensíveis
                is_sens = False
                for rota in ["/admin", "/backup", "/config", "/private"]:
                    if rota == c_recurso: is_sens = True
                if is_sens:
                    sens_total += 1
                    if c_status != "200": 
                        sens_falhas += 1
                        if c_recurso == "/admin": admin_indevido += 1

                ip_mais = max(cont_ip, key=cont_ip.get)
                rec_mais = max(cont_rec, key=cont_rec.get)

        # Cálculos Finais
        disp = (sucessos / total) * 100 if total > 0 else 0
        taxa_e = (erros / total) * 100 if total > 0 else 0
        media_t = soma_tempo / total if total > 0 else 0
        
        estado = "SAUDÁVEL"
        if fc_total >= 1 or disp < 70: estado = "CRÍTICO"
        elif disp < 85 or qtd_lento > (total * 0.3): estado = "INSTÁVEL"
        elif disp < 95 or fb_total > 0 or bot_total > 0: estado = "ATENÇÃO"

        # Relatório Final
        separador = "=" * 50
        linha = "-" * 50

        print("\n" + separador)
        print("          RELATÓRIO MONITOR LOGPY")
        print(separador)
        print(f"Total de acessos: {total}")
        print(f"Estado final: {estado}")
        print()

        print("[VISÃO GERAL]")
        print(f"Sucessos: {sucessos}")
        print(f"Erros: {erros} | Críticos: {erros_500}")
        print(f"Disponibilidade: {disp:.2f}%")
        print(f"Taxa de erro: {taxa_e:.2f}%")
        print()

        print("[DESEMPENHO]")
        print(f"Tempo médio: {media_t:.2f} ms")
        print(f"Maior tempo: {maior_t} ms")
        print(f"Menor tempo: {menor_t} ms")
        print(f"Rápidos: {qtd_rapido} | Normais: {qtd_normal} | Lentos: {qtd_lento}")
        print()

        print("[STATUS HTTP]")
        print(f"200: {st_200}   403: {st_403}   404: {st_404}   500: {st_500}")
        print(f"Recurso mais ativo: {rec_mais}")
        print(f"IP mais ativo: {ip_mais}")
        print()

        print("[SEGURANÇA]")
        print(f"Força bruta: {fb_total} | Último IP: {fb_ultimo}")
        print(f"Acessos indevidos em /admin: {admin_indevido}")
        print(f"Eventos de degradação: {deg_total}")
        print(f"Eventos de falha crítica: {fc_total}")
        print(f"Suspeitas de bot: {bot_total} | Último IP: {bot_ultimo}")
        print(f"Rotas sensíveis: {sens_total} | Falhas: {sens_falhas}")
        print(separador)

    except FileNotFoundError:
        print("\n[ERRO] Arquivo não encontrado. Gere os logs primeiro.")

# MENU INTERATIVO

def menu():
    arquivo = "log_coderslabs.txt"
    while True:
        print("\n--- MENU MONITOR LOGPY ---")
        print("1. Gerar logs")
        print("2. Analisar logs")
        print("3. Gerar e analisar")
        print("4. Sair")
        
        escolha = input("Escolha uma opção: ").strip()
        
        if escolha == '1':
            try:
                n = int(input("Qtd de logs: "))
                gerar_arquivo_logs(arquivo, n)
            except ValueError:
                print("Entrada inválida! Digite um número inteiro.")
            except Exception as erro:
                print(f"[ERRO] Falha ao gerar logs: {erro}")
        elif escolha == '2':
            analisar_arquivo_logs(arquivo)
        elif escolha == '3':
            try:
                n = int(input("Qtd de logs: "))
                gerar_arquivo_logs(arquivo, n)
                analisar_arquivo_logs(arquivo)
            except ValueError:
                print("Entrada inválida! Digite um número inteiro.")
            except Exception as erro:
                print(f"[ERRO] Falha ao gerar/analisar logs: {erro}")
        elif escolha == '4':
            print("Saindo..."); break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    menu()
