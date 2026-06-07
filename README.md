# A/B Testing Demo — ISA2

## ¿Qué es esto?

Proyecto de demostración para la materia ISA2 que ilustra cómo implementar un experimento de A/B testing en una aplicación web real. La app sirve dos variantes de una landing page de compra (control vs. tratamiento) y registra visitas, clics y tiempo de decisión usando Prometheus. Grafana muestra los resultados en tiempo real, convirtiendo el experimento en un sistema observable de extremo a extremo.

## Concepto

- **Hipótesis:** una página con urgencia, descuento visible y prueba social (Variante B) genera mayor tasa de conversión que un diseño limpio y sin presión (Variante A).
- **Asignación aleatoria y sticky:** al primer acceso, el servidor asigna la variante al azar y la persiste en una cookie de 30 días; visitas posteriores del mismo usuario siempre ven la misma variante.
- **La telemetría es el árbitro:** sin métricas instrumentadas no hay forma de saber qué variante funciona mejor; Prometheus captura cada evento y Grafana hace visible el impacto en tiempo real.

## Stack

- **Flask** — backend + lógica del experimento
- **Prometheus** — scraping de métricas cada 5 s
- **Grafana** — dashboard con 6 paneles preconfigurados
- **Docker Compose** — un solo comando para levantar todo

## Cómo correrlo

```bash
docker compose up --build
# App:      http://localhost:5000
# Grafana:  http://localhost:3000  (admin / admin)
# Metrics:  http://localhost:5000/metrics
```

## Rutas útiles para la demo

| Ruta | Descripción |
|------|-------------|
| `/force/A` | Forzar variante A (control) |
| `/force/B` | Forzar variante B (tratamiento) |
| `/simulate` | Generar tráfico sintético (POST) |
| `/metrics` | Endpoint scrapeado por Prometheus |

## Correr el simulador

```bash
pip install requests
python simulate.py
# Variante A: 50 visitas, 20% conversión
# Variante B: 50 visitas, 40% conversión
```

## Métricas implementadas

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `ab_page_visits_total{variant}` | Counter | Visitas por variante |
| `ab_buy_clicks_total{variant}` | Counter | Compras por variante |
| `ab_time_to_convert_seconds{variant}` | Histogram | Segundos hasta la compra |

## Qué muestra el dashboard

- Tasa de conversión A vs B en tiempo real
- Volumen de tráfico balanceado
- Tiempo de decisión (p50 y p90) por variante
