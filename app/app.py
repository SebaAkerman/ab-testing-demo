import random
import time

from flask import Flask, request, make_response, render_template, jsonify
from prometheus_client import Counter, Histogram, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

COOKIE_VARIANT = "ab_variant"
COOKIE_TS = "ab_visit_ts"
VARIANTS = ["A", "B"]
COOKIE_MAX_AGE = 30 * 24 * 3600

page_visits_total = Counter(
    "ab_page_visits_total",
    "Total page visits per variant",
    ["variant"],
)

buy_clicks_total = Counter(
    "ab_buy_clicks_total",
    "Total buy-button clicks per variant",
    ["variant"],
)

time_to_convert = Histogram(
    "ab_time_to_convert_seconds",
    "Seconds between first visit and buy click per variant",
    ["variant"],
    buckets=[5, 15, 30, 60, 120],
)

flask_app = Flask(__name__)


@flask_app.route("/")
def index():
    variant = request.cookies.get(COOKIE_VARIANT)
    ts = request.cookies.get(COOKIE_TS)
    is_new = variant is None

    if is_new:
        variant = random.choice(VARIANTS)

    page_visits_total.labels(variant=variant).inc()

    template = "variant_a.html" if variant == "A" else "variant_b.html"
    resp = make_response(render_template(template, variant=variant))

    if is_new:
        resp.set_cookie(COOKIE_VARIANT, variant, max_age=COOKIE_MAX_AGE, httponly=True)
        resp.set_cookie(COOKIE_TS, str(time.time()), max_age=COOKIE_MAX_AGE)

    return resp


@flask_app.route("/buy", methods=["POST"])
def buy():
    variant = request.cookies.get(COOKIE_VARIANT, "unknown")
    ts = request.cookies.get(COOKIE_TS)

    elapsed = None
    if ts:
        try:
            elapsed = time.time() - float(ts)
            time_to_convert.labels(variant=variant).observe(elapsed)
        except ValueError:
            pass

    buy_clicks_total.labels(variant=variant).inc()
    return render_template("thank_you.html", variant=variant, elapsed=elapsed)


@flask_app.route("/simulate", methods=["POST"])
def simulate():
    data = request.get_json(force=True)
    variant = data.get("variant", "A")
    visits = int(data.get("visits", 0))
    clicks = int(data.get("clicks", 0))
    avg_seconds = float(data.get("avg_seconds", 30))

    for _ in range(visits):
        page_visits_total.labels(variant=variant).inc()

    for _ in range(clicks):
        buy_clicks_total.labels(variant=variant).inc()
        # Gaussian noise around avg_seconds, clamped to positive
        duration = max(1.0, avg_seconds + random.gauss(0, 5))
        time_to_convert.labels(variant=variant).observe(duration)

    return jsonify({"variant": variant, "visits": visits, "clicks": clicks, "avg_seconds": avg_seconds})


application = DispatcherMiddleware(flask_app, {"/metrics": make_wsgi_app()})

if __name__ == "__main__":
    run_simple("0.0.0.0", 5000, application)
