# 📄 Processador de Arquivos XML

Script Python para processar arquivos XML em lote, substituindo caracteres específicos e organizando arquivos automaticamente.

---

## 🎯 O que este script faz?

Este script automatiza o processamento de arquivos XML realizando as seguintes tarefas:

1. **Localiza todos os arquivos `.xml`** no diretório atual
2. **Busca pelo elemento `<xTexto>`** em cada arquivo
3. **Substitui o caractere `É` por `E`** no conteúdo do elemento
4. **Repara XMLs malformados** automaticamente quando possível
5. **Cria backups** de todos os arquivos alterados
6. **Organiza arquivos** em pastas específicas conforme o resultado do processamento

---

## 📁 Estrutura de Pastas Criadas

Após a execução, o script organiza os arquivos nas seguintes pastas:

| Pasta | Conteúdo |
|-------|----------|
| `📂 Backup_XML/` | Cópias de segurança dos arquivos alterados |
| `📂 xmls_nao_alterados/` | XMLs válidos mas que não continham o caractere `É` |
| `📂 Arquivos_NOT_alterados/` | XMLs com erros de parse, elementos vazios ou inválidos |
| `📂 (diretório atual)` | Apenas os arquivos que foram alterados com sucesso |

---

## 🔧 Problemas que o Script Resolve

### ✅ XMLs Malformados
- **Problema:** Tags não fechadas, caracteres inválidos, estrutura quebrada
- **Solução:** Tentativa automática de reparo usando `lxml` ou correções manuais

### ✅ Processamento em Lote
- **Problema:** Precisar alterar dezenas/centenas de XMLs manualmente
- **Solução:** Processa todos os arquivos de uma vez

### ✅ Segurança dos Dados
- **Problema:** Risco de perder arquivos originais
- **Solução:** Backup automático antes de qualquer alteração

### ✅ Organização
- **Problema:** Arquivos misturados após processamento
- **Solução:** Separação automática por categoria

---

## 📋 Pré-requisitos

- **Python 3.8+** instalado
- Bibliotecas Python (instalação abaixo)

---

## 🚀 Como Instalar

### 1. Instalar Dependências Básicas

```bash
pip install defusedxml
```

### 2. Instalar Biblioteca para Reparo de XMLs (Opcional, mas Recomendado)

```bash
pip install lxml
```

**Por que instalar?**
- `defusedxml`: Protege contra vulnerabilidades de segurança em XMLs
- `lxml`: Permite reparar automaticamente XMLs malformados

---

## 💻 Como Executar

### **Método 1: Linha de Comando**

```bash
# Navegue até a pasta com os arquivos XML
cd C:\Users\seu_usuario\Documents\AUTOMATIZA_AÊ

# Execute o script
python index.py
```

### **Método 2: Criar Arquivo .bat (Windows)**

Crie um arquivo `ProcessadorXML.bat` na mesma pasta do script:

```batch
@echo off
cd /d "%~dp0"
python index.py
pause
```

Agora basta dar **duplo clique** no arquivo `.bat`!

### **Método 3: Gerar Executável (.exe)**

```bash
# Instalar PyInstaller
pip install pyinstaller

# Gerar executável
python -m PyInstaller --onefile --name ProcessadorXML index.py

# O executável estará em: dist/ProcessadorXML.exe
```

---

## ⚙️ Configurações Disponíveis

Edite as configurações no início da função `main()`:

```python
config = Config(
    old_value="É",              # Caractere a ser substituído
    new_value="E",              # Novo caractere
    target_element="xTexto",    # Nome do elemento XML alvo
    try_repair=True,            # Tentar reparar XMLs malformados
    create_backup=True,         # Criar backups
    dry_run=False,              # True = apenas simula, não altera
    log_level="INFO"            # DEBUG para mais detalhes
)
```

### 🧪 Modo de Teste (Dry Run)

Para testar sem alterar arquivos:

```python
config = Config(
    dry_run=True,  # Apenas mostra o que seria feito
    log_level="DEBUG"
)
```

---

## 📊 Saída do Programa

### Durante a Execução:

```
21:40:05 - INFO - 🚀 Iniciando processamento em: C:\Users\...\AUTOMATIZA_AÊ
21:40:05 - INFO - 📄 Encontrados 25 arquivo(s) XML
21:40:05 - INFO - 📂 XMLs com erro/vazios: Arquivos_NOT_alterados
21:40:05 - INFO - 📂 XMLs sem 'É': xmls_nao_alterados
21:40:05 - INFO - 💾 Pasta de backup: Backup_XML
21:40:06 - INFO - 🔧 XML reparado com sucesso: xml1.xml
21:40:06 - INFO - ✓ Alterado 'xml1.xml': 3 substituição(ões)
21:40:07 - INFO - ○ 'É' não encontrado: xml2.xml
```

### Resumo Final:

```
============================================================
📊 RESUMO DO PROCESSAMENTO
============================================================
✓ Arquivos alterados: 15
○ 'É' não encontrado: 8
⊘ Elementos vazios/ausentes: 2
🔧 XMLs reparados: 5

📁 Total processado: 25 arquivo(s)
💾 Backups salvos em: Backup_XML
============================================================
```

---

## 🐛 Solução de Problemas

### Erro: `pip: command not found`

**Solução:**
```bash
python -m pip install defusedxml
```

### Erro: `pyinstaller: command not found`

**Solução:**
```bash
python -m PyInstaller --onefile --name ProcessadorXML index.py
```

### XMLs ainda não são reparados

**Solução:** Instale o `lxml`:
```bash
pip install lxml
```

### Terminal fecha muito rápido

O script já possui `input()` no final para manter o terminal aberto. Se usar .bat, adicione `pause` no final.

---

## 📝 Exemplo de Uso

### Antes:
```
📂 Pasta_Projeto/
  ├── xml1.xml  (contém "É")
  ├── xml2.xml  (contém "É")
  ├── xml3.xml  (não contém "É")
  ├── xml4.xml  (malformado)
  └── index.py
```

### Depois:
```
📂 Pasta_Projeto/
  ├── xml1.xml  (alterado: É → E)
  ├── xml2.xml  (alterado: É → E)
  ├── index.py
  ├── 📂 Backup_XML/
  │   ├── xml1.xml
  │   └── xml2.xml
  ├── 📂 xmls_nao_alterados/
  │   └── xml3.xml
  └── 📂 Arquivos_NOT_alterados/
      └── xml4.xml
```

---

## 🔒 Segurança

- ✅ Usa `defusedxml` para proteção contra ataques XXE
- ✅ Cria backups automáticos antes de qualquer alteração
- ✅ Move arquivos problemáticos para pastas separadas (não deleta)
- ✅ Evita sobrescrever arquivos existentes nas pastas de destino

---

## 📄 Licença

Este script é fornecido "como está", sem garantias. Use por sua conta e risco.

---

## 👨‍💻 Suporte

Para problemas ou dúvidas:
1. Verifique se todas as dependências estão instaladas
2. Execute com `log_level="DEBUG"` para mais detalhes
3. Teste com `dry_run=True` antes de processar arquivos importantes

---

## 🎯 Próximas Melhorias Possíveis

- [ ] Interface gráfica (GUI)
- [ ] Processamento recursivo de subpastas
- [ ] Múltiplas substituições simultâneas
- [ ] Relatório em HTML/PDF
- [ ] Agendamento automático

---

**Versão:** 3.0  
**Última atualização:** Outubro 2025