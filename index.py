import os
import xml.etree.ElementTree as ET
import shutil

def lista_arquivos_diretorio():
    caminho_diretorio = "."
    arquivos = os.listdir(caminho_diretorio)
    return filtro_arquivos_xml(arquivos)

def filtro_arquivos_xml(itens):
    xmls = []
    for item in itens:
        separado = item.split(".")
        if "xml" in separado:
            print(item)
            xmls.append(item)
        else:
            print("skipping")
    return xmls

def cria_pasta_arquivos_nao_alterados():
    pasta = "Arquivos_NOT_alterados"
    os.makedirs(pasta, exist_ok=True)  # Adicione exist_ok=True para evitar erro se já existir
    return os.path.abspath(pasta)

def __init__():
    arquivos_alterados = 0
    arquivos_nao_alterados = 0

    xmls = lista_arquivos_diretorio()

    cria_pasta_arquivos_nao_alterados()

    leitura = ""
    #  for arquivo in xmls:
    #     leitura = ET.parse(arquivo)
    #     raiz = leitura.getroot()
    #     xTexto = raiz.find("xTexto") 
    #     if xTexto:
    #         xTexto.find("É").text.replace("É", "E")
    #         arquivos_alterados += 1
    #         print("PASSEI AQUI!")
    #     else:
    #         arquivos_nao_alterados += 1
    #         pasta = cria_pasta_arquivos_nao_alterados()
    #         shutil.move(arquivo, os.path.join(pasta, arquivo))
    # print("ARQUIVOS XML ALTERADOS COM SUCESSO")
    print(xmls)
    
    print(f"XML's ALTERADOS: {arquivos_alterados}")
    print(f"XML's NÃO ALTERADOS: {arquivos_nao_alterados}")

__init__()