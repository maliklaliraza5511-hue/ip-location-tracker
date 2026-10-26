"""Local Flask web dashboard for IP Location Tracker."""
from flask import Flask, flash, redirect, render_template_string, request, url_for
from tracker_core import get_history, lookup_ip

app = Flask(__name__)
app.secret_key = "local-development-key-change-before-sharing"

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IP Location Tracker</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root{color-scheme:dark;--bg:#0b1220;--card:#121d30;--line:#26364d;--accent:#38bdf8;--muted:#a8b5c7}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#14243a,var(--bg) 55%);color:#e7eef8;font:16px system-ui,sans-serif}
main{max-width:1100px;margin:auto;padding:28px 18px}.top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
h1{margin:0;font-size:clamp(1.7rem,4vw,2.5rem)}.muted{color:var(--muted)}.pill{border:1px solid #23516a;color:#7dd3fc;padding:6px 10px;border-radius:99px}
.card{background:rgba(18,29,48,.94);border:1px solid var(--line);border-radius:18px;padding:20px;margin-top:20px;box-shadow:0 12px 30px #0002}
form.search{display:flex;gap:10px;flex-wrap:wrap}input{flex:1;min-width:220px;background:#0a1322;color:white;border:1px solid #344760;border-radius:10px;padding:13px;font-size:1rem}
button{background:var(--accent);color:#082032;border:0;border-radius:10px;padding:13px 18px;font-weight:750;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.stat{background:#0b1627;border:1px solid var(--line);padding:14px;border-radius:12px;overflow-wrap:anywhere}.stat small{display:block;color:var(--muted);margin-bottom:6px}.stat strong{font-size:1.03rem}
#map{height:340px;border-radius:12px;background:#0b1627}.tablewrap{overflow:auto}table{width:100%;border-collapse:collapse;min-width:650px}th,td{text-align:left;border-bottom:1px solid var(--line);padding:11px}th{color:#7dd3fc}
.notice{background:#3b1e22;border:1px solid #79353c;padding:12px;border-radius:10px;margin:12px 0}.foot{font-size:.9rem;color:var(--muted);line-height:1.6}
</style></head><body><main>
<div class="top"><div><h1>IP Location Tracker</h1><p class="muted">Local dashboard · IPv4 / IPv6 · reports and history</p></div><span class="pill">KALI LINUX</span></div>
<section class="card"><h2>Lookup public IP</h2>
<form class="search" method="post" action="{{ url_for('index') }}"><input name="ip" placeholder="e.g. 8.8.8.8" value="{{ searched or '' }}" required><button type="submit">Look up IP</button></form>
{% for message in get_flashed_messages() %}<div class="notice">{{ message }}</div>{% endfor %}
{% if result %}
<h2>Result: {{ result.ip }}</h2><div class="grid">
{% for label,key in [('Country','country'),('Region','region'),('City','city'),('ISP','isp'),('Organization','organization'),('ASN','asn'),('Latitude','latitude'),('Longitude','longitude'),('Timezone','timezone'),('IP Version','version'),('Postal code','postal_code'),('Lookup time','looked_up_at')] %}
<div class="stat"><small>{{ label }}</small><strong>{{ result[key] if result[key] is not none else 'N/A' }}</strong></div>
{% endfor %}</div>
{% if result.latitude is not none and result.longitude is not none %}<h3>Approximate location</h3><div id="map"></div><p><a target="_blank" rel="noopener" href="https://www.openstreetmap.org/?mlat={{result.latitude}}&mlon={{result.longitude}}#map=12/{{result.latitude}}/{{result.longitude}}">Open in OpenStreetMap</a></p>{% endif %}
<p class="foot">TXT, JSON and CSV reports were saved locally.</p>
{% endif %}</section>
<section class="card"><h2>Recent lookup history</h2>{% if history %}<div class="tablewrap"><table><thead><tr><th>Time</th><th>IP</th><th>City / Country</th><th>ISP</th><th>Coordinates</th></tr></thead><tbody>
{% for row in history %}<tr><td>{{row.looked_up_at}}</td><td>{{row.ip}}</td><td>{{row.city}}, {{row.country}}</td><td>{{row.isp}}</td><td>{{row.latitude if row.latitude is not none else 'N/A'}}, {{row.longitude if row.longitude is not none else 'N/A'}}</td></tr>{% endfor %}
</tbody></table></div>{% else %}<p class="muted">No lookups yet. Search a public IP to begin.</p>{% endif %}</section>
<p class="foot">IP geolocation is approximate and may identify an ISP gateway or city rather than a person's exact location. Lookups are sent to the third-party ipwho.is API. History and reports are stored on this computer.</p>
</main>
{% if result and result.latitude is not none and result.longitude is not none %}
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const lat={{result.latitude|tojson}}, lon={{result.longitude|tojson}};
const map=L.map('map').setView([lat,lon],10);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; OpenStreetMap'}).addTo(map);
L.marker([lat,lon]).addTo(map).bindPopup('Approximate IP location').openPopup();
</script>{% endif %}
</body></html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    searched = ""
    if request.method == "POST":
        searched = request.form.get("ip", "").strip()
        try:
            result = lookup_ip(searched)
        except (ValueError, RuntimeError) as exc:
            flash(str(exc))
    return render_template_string(PAGE, result=result, searched=searched, history=get_history(25))

if __name__ == "__main__":
    # Bind to localhost only; do not expose this development dashboard to a network.
    app.run(host="127.0.0.1", port=5000, debug=False)
