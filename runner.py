import time
import scraper

INTERVALO = 30 * 60  # 30 minutos

while True:
    print("Atualizando feed...")
    scraper.gerar_feed()
    print("Aguardando", INTERVALO/60, "minutos...")
    time.sleep(INTERVALO)
