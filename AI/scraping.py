import os
import time
import random
from urllib.parse import urljoin, urldefrag
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client
from playwright.sync_api import sync_playwright

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
URL_BASE = "https://elglobusvermell.org/"

def rastrear_modo_ninja():
    
    urls_pendientes = [URL_BASE]
    urls_visitadas = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()
        
        while urls_pendientes:
            url_actual = urls_pendientes.pop(0)
            url_actual, _ = urldefrag(url_actual)
            url_actual = url_actual.rstrip('/')
            url_actual = url_actual.replace("http://", "https://")
            
            if url_actual in urls_visitadas:
                continue
                
            urls_visitadas.add(url_actual)
            
            try:
                print(f" [{len(urls_visitadas)}] Infiltrándonos en: {url_actual}")
                
                page.goto(url_actual, wait_until="domcontentloaded", timeout=30000)
                
                #  Ahora esperamos entre 5 y 10 segundos. Paciencia de monje.
                descanso = random.uniform(5.0, 10.0)
                print(f"   💤 Descansando {descanso:.1f} segundos para parecer humanos...")
                time.sleep(descanso)
                
                html_procesado = page.content()
                
                if "We're sorry, you are not allowed to proceed" in html_procesado or "Wordfence" in html_procesado:
                    print(f"¡ALERTA! Escondiéndonos 30 segundos...")
                    time.sleep(30)
                    continue 
                
                soup = BeautifulSoup(html_procesado, 'html.parser')
                
                for ruido in soup(["header", "footer", "nav", "aside", "script", "style", "form", "iframe"]):
                    ruido.extract()
                
                etiquetas = soup.find_all(['h1', 'h2', 'h3', 'p', 'li'])
                texto_bruto = " ".join([et.get_text(separator=' ', strip=True) for et in etiquetas])
                texto_final = " ".join(texto_bruto.split())
                
                if len(texto_final) > 100:
                    supabase.table("info_web").upsert({
                        "url": url_actual, 
                        "contenido": texto_final[:5000]
                    }).execute()

                for enlace in soup.find_all('a', href=True):
                    href_completo = urljoin(URL_BASE, enlace['href'])
                    href_limpio, _ = urldefrag(href_completo)
                    href_limpio = href_limpio.rstrip('/')
                    href_limpio = href_limpio.replace("http://", "https://")
                    
                    es_interno = "elglobusvermell.org" in href_limpio
                    
                    if es_interno and href_limpio not in urls_visitadas and href_limpio not in urls_pendientes:
                        extensiones_prohibidas = ['.pdf', '.jpg', '.png', '.zip', '.doc', '.docx', '.mp4', '.mp3', '.jpeg']
                        if not any(href_limpio.lower().endswith(ext) for ext in extensiones_prohibidas):
                            urls_pendientes.append(href_limpio)
                        
            except Exception as e:
                print(f" Se saltará {url_actual} por un error: {e}")

        browser.close()
        
    print(" ¡MISIÓN CUMPLIDA, BB!")

if __name__ == '__main__':
    rastrear_modo_ninja()