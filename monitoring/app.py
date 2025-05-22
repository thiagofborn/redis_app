from flask import Flask, jsonify, render_template
import redis

app = Flask(__name__)
valkey_client = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/')
def monitor_page():
    return render_template('monitor.html')

@app.route('/api/ttls')
def get_key_ttls():
    keys = valkey_client.keys('*')  # Use a more specific pattern in prod
    key_ttls = {}
    for key in keys:
        ttl = valkey_client.ttl(key)
        key_ttls[key.decode()] = ttl if ttl >= 0 else 'No expiry'
    return jsonify(key_ttls)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5010)

