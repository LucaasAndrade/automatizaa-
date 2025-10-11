#!/usr/bin/env python3
"""
Script para processar arquivos XML:
- Localiza arquivos .xml no diretório atual
- Substitui 'É' por 'E' em elementos <xTexto>
- Move arquivos não alterados para pasta separada
- Tenta recuperar XMLs malformados

Melhorias v3:
- Recuperação automática de XMLs malformados
- Backup antes de alterações
- Análise detalhada de erros
- Modo de reparo de XMLs
"""

from pathlib import Path
import shutil
import logging
import re
from typing import Optional
from dataclasses import dataclass
from collections import Counter

try:
    from defusedxml import ElementTree as ET
    USING_DEFUSED = True
except ImportError:
    import xml.etree.ElementTree as ET
    USING_DEFUSED = False


@dataclass
class Config:
    """Configurações centralizadas do processamento."""
    error_folder: str = "xml_nao_alterados"  # XMLs com erro/vazio
    no_match_folder: str = "xmls_corrigidos"  # XMLs sem 'É' encontrado
    backup_folder: str = "Backup_XML"
    old_value: str = "É"
    new_value: str = "E"
    target_element: str = "xTexto"
    dry_run: bool = False
    try_repair: bool = True  # Tenta reparar XMLs malformados
    create_backup: bool = True  # Cria backup antes de alterar
    log_level: str = "INFO"


class XMLProcessor:
    """Classe para processar arquivos XML com substituição de texto."""
    
    def __init__(self, config: Config):
        self.config = config
        self.stats = Counter()
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura o sistema de logging."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S"
        )
        
        if not USING_DEFUSED:
            logging.warning(
                "⚠️  'defusedxml' não instalado. "
                "Recomenda-se instalar: pip install defusedxml"
            )
    
    def list_xml_files(self, directory: Path) -> list[Path]:
        """Lista arquivos XML no diretório."""
        files = sorted([
            p for p in directory.iterdir() 
            if p.is_file() and p.suffix.lower() == ".xml"
        ])
        logging.info(f"📄 Encontrados {len(files)} arquivo(s) XML")
        return files
    
    def create_folder(self, base_dir: Path, folder_name: str) -> Path:
        """Cria pasta se necessário."""
        folder = base_dir / folder_name
        if not self.config.dry_run:
            folder.mkdir(parents=True, exist_ok=True)
        return folder.resolve()
    
    def create_backup(self, file_path: Path, backup_folder: Path) -> Optional[Path]:
        """Cria backup do arquivo antes de modificar."""
        if not self.config.create_backup or self.config.dry_run:
            return None
        
        try:
            backup_path = backup_folder / file_path.name
            if backup_path.exists():
                base, suffix = backup_path.stem, backup_path.suffix
                counter = 1
                while (new_backup := backup_folder / f"{base}_{counter}{suffix}").exists():
                    counter += 1
                backup_path = new_backup
            
            shutil.copy2(str(file_path), str(backup_path))
            logging.debug(f"💾 Backup criado: {backup_path.name}")
            return backup_path
        except Exception as e:
            logging.error(f"❌ Falha ao criar backup de '{file_path.name}': {e}")
            return None
    
    def try_repair_xml(self, file_path: Path) -> Optional[str]:
        """
        Tenta reparar XML malformado fazendo parse com lxml em modo recover,
        ou aplicando correções simples de texto.
        """
        if not self.config.try_repair:
            return None
        
        try:
            # Tenta com lxml que tem modo de recuperação
            try:
                from lxml import etree as lxml_et
                parser = lxml_et.XMLParser(recover=True, encoding='utf-8')
                tree = lxml_et.parse(str(file_path), parser)
                
                # Converte de volta para string
                repaired = lxml_et.tostring(
                    tree.getroot(), 
                    encoding='unicode', 
                    pretty_print=True
                )
                
                logging.info(f"🔧 XML reparado com lxml: {file_path.name}")
                self.stats['repaired_lxml'] += 1
                return repaired
                
            except ImportError:
                # Se lxml não estiver disponível, tenta correções básicas
                logging.debug("lxml não disponível, tentando correção manual")
                return self._manual_repair(file_path)
                
        except Exception as e:
            logging.debug(f"Reparo falhou para '{file_path.name}': {e}")
            return None
    
    def _manual_repair(self, file_path: Path) -> Optional[str]:
        """Tenta correções manuais simples em XMLs malformados."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Correção 1: Remove caracteres de controle inválidos
            content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', content)
            
            # Correção 2: Fecha tags não fechadas (básico)
            # Procura padrão de tag aberta sem fechamento
            open_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*>', content)
            close_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)>', content)
            
            # Identifica tags não fechadas
            from collections import Counter as CounterColl
            open_count = CounterColl(open_tags)
            close_count = CounterColl(close_tags)
            
            unclosed = {tag: count - close_count.get(tag, 0) 
                       for tag, count in open_count.items() 
                       if count > close_count.get(tag, 0)}
            
            # Adiciona fechamentos no final (antes da tag raiz fechar)
            if unclosed:
                # Encontra última tag de fechamento
                last_close = content.rfind('</')
                if last_close > 0:
                    closing_tags = ''.join(f'</{tag}>' for tag in unclosed.keys())
                    content = content[:last_close] + closing_tags + content[last_close:]
                    
                    logging.info(f"🔧 Correção manual aplicada: {file_path.name}")
                    self.stats['repaired_manual'] += 1
                    return content
            
            if content != original_content:
                logging.info(f"🔧 Caracteres inválidos removidos: {file_path.name}")
                self.stats['repaired_manual'] += 1
                return content
            
        except Exception as e:
            logging.debug(f"Correção manual falhou: {e}")
        
        return None
    
    def find_element_by_local_name(
        self, 
        root: ET.Element, 
        local_name: str
    ) -> Optional[ET.Element]:
        """
        Busca elemento por nome local, ignorando namespaces.
        Suporta tags como {namespace}localname.
        """
        for el in root.iter():
            if el.tag.split('}')[-1] == local_name:
                return el
        return None
    
    def safe_move(self, src: Path, dst: Path) -> None:
        """Move arquivo evitando sobrescrever destinos existentes."""
        if self.config.dry_run:
            logging.info(f"[DRY-RUN] Moveria: {src.name} → {dst.parent.name}/")
            return
        
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        if dst.exists():
            base, suffix = dst.stem, dst.suffix
            counter = 1
            while (new_dst := dst.parent / f"{base}_{counter}{suffix}").exists():
                counter += 1
            dst = new_dst
        
        shutil.move(str(src), str(dst))
        logging.debug(f"Movido: {src.name} → {dst}")
    
    def process_file(self, file_path: Path, error_folder: Path, no_match_folder: Path, backup_folder: Path) -> bool:
        """
        Processa um arquivo XML individual.
        Retorna True se houve alteração, False caso contrário.
        """
        tree = None
        repaired_content = None
        
        # Primeira tentativa de parse
        try:
            tree = ET.parse(str(file_path))
            root = tree.getroot()
            
        except ET.ParseError as e:
            logging.warning(f"⚠️  Parse falhou '{file_path.name}': {e}")
            
            # Tenta reparar
            repaired_content = self.try_repair_xml(file_path)
            
            if repaired_content:
                # Salva versão reparada temporariamente
                try:
                    from io import StringIO
                    tree = ET.parse(StringIO(repaired_content))
                    root = tree.getroot()
                    logging.info(f"✓ XML reparado com sucesso: {file_path.name}")
                except Exception as repair_error:
                    logging.error(f"❌ Reparo falhou '{file_path.name}': {repair_error}")
                    self.stats['parse_error'] += 1
                    self.safe_move(file_path, error_folder / file_path.name)
                    return False
            else:
                logging.error(f"❌ Impossível reparar '{file_path.name}'")
                self.stats['parse_error'] += 1
                self.safe_move(file_path, error_folder / file_path.name)
                return False
            
        except Exception as e:
            logging.error(f"❌ Erro inesperado '{file_path.name}': {e}")
            self.stats['unexpected_error'] += 1
            self.safe_move(file_path, error_folder / file_path.name)
            return False
        
        # Busca elemento alvo
        xtexto = self.find_element_by_local_name(root, self.config.target_element)
        
        if xtexto is None or not (xtexto.text and xtexto.text.strip()):
            logging.info(f"⊘ Elemento <{self.config.target_element}> vazio: {file_path.name}")
            self.stats['empty_element'] += 1
            self.safe_move(file_path, error_folder / file_path.name)
            return False
        
        # Verifica necessidade de alteração
        old_text = xtexto.text
        new_text = old_text.replace(self.config.old_value, self.config.new_value)
        
        if new_text == old_text:
            logging.info(f"○ '{self.config.old_value}' não encontrado: {file_path.name}")
            self.stats['no_match'] += 1
            self.safe_move(file_path, no_match_folder / file_path.name)
            return False
        
        # Aplica alteração
        replacements = old_text.count(self.config.old_value)
        xtexto.text = new_text
        
        if self.config.dry_run:
            logging.info(
                f"[DRY-RUN] Alteraria '{file_path.name}': "
                f"{replacements} ocorrência(s) de '{self.config.old_value}'"
            )
            self.stats['would_change'] += 1
            return True
        
        # Cria backup antes de salvar
        self.create_backup(file_path, backup_folder)
        
        try:
            # Se foi reparado, salva a versão reparada
            if repaired_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                    # Remove declaração XML se já existir no conteúdo reparado
                    content_to_write = re.sub(r'<\?xml[^>]+\?>\s*', '', repaired_content)
                    f.write(content_to_write)
            else:
                tree.write(
                    str(file_path), 
                    encoding="utf-8", 
                    xml_declaration=True,
                    method="xml"
                )
            
            logging.info(f"✓ Alterado '{file_path.name}': {replacements} substituição(ões)")
            self.stats['changed'] += 1
            return True
            
        except Exception as e:
            logging.error(f"❌ Falha ao salvar '{file_path.name}': {e}")
            self.stats['save_error'] += 1
            self.safe_move(file_path, error_folder / file_path.name)
            return False
    
    def print_summary(self):
        """Exibe resumo do processamento."""
        total = sum(self.stats.values())
        
        print("\n" + "="*60)
        print("📊 RESUMO DO PROCESSAMENTO")
        print("="*60)
        
        if self.config.dry_run:
            print(f"✓ Arquivos que seriam alterados: {self.stats['would_change']}")
        else:
            print(f"✓ Arquivos alterados: {self.stats['changed']}")
        
        print(f"○ '{self.config.old_value}' não encontrado: {self.stats['no_match']}")
        print(f"⊘ Elementos vazios/ausentes: {self.stats['empty_element']}")
        
        if self.stats['repaired_lxml'] or self.stats['repaired_manual']:
            repaired = self.stats['repaired_lxml'] + self.stats['repaired_manual']
            print(f"🔧 XMLs reparados: {repaired}")
        
        if self.stats['parse_error']:
            print(f"❌ Erros de parse: {self.stats['parse_error']}")
        if self.stats['save_error']:
            print(f"❌ Erros ao salvar: {self.stats['save_error']}")
        if self.stats['unexpected_error']:
            print(f"❌ Erros inesperados: {self.stats['unexpected_error']}")
        
        print(f"\n📁 Total processado: {total} arquivo(s)")
        
        if self.config.create_backup and not self.config.dry_run:
            print(f"💾 Backups salvos em: {self.config.backup_folder}")
        
        print("="*60)
    
    def run(self, directory: Path = Path('.')):
        """Executa o processamento completo."""
        base_dir = directory.resolve()
        
        mode = "[MODO DRY-RUN] " if self.config.dry_run else ""
        logging.info(f"🚀 {mode}Iniciando processamento em: {base_dir}")
        
        xml_files = self.list_xml_files(base_dir)
        
        if not xml_files:
            logging.warning("⚠️  Nenhum arquivo XML encontrado no diretório")
            return
        
        error_folder = self.create_folder(base_dir, self.config.error_folder)
        no_match_folder = self.create_folder(base_dir, self.config.no_match_folder)
        backup_folder = self.create_folder(base_dir, self.config.backup_folder)
        
        logging.info(f"📂 XMLs com erro/vazios: {error_folder.name}")
        logging.info(f"📂 XMLs sem '{self.config.old_value}': {no_match_folder.name}")
        if self.config.create_backup:
            logging.info(f"💾 Pasta de backup: {backup_folder.name}")
        
        for xml_file in xml_files:
            self.process_file(xml_file, error_folder, no_match_folder, backup_folder)
        
        self.print_summary()


def main():
    """Ponto de entrada principal."""
    config = Config(
        try_repair=True,  # Ativa reparo automático
        create_backup=True,  # Cria backups
        # Descomente para teste sem alterações:
        # dry_run=True,
        # log_level="DEBUG"
    )
    
    processor = XMLProcessor(config)
    processor.run()


if __name__ == "__main__":
    main()