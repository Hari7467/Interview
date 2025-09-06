def log_request(service_name, method, url, status_code, duration_ms):
    print(
        f"[GATEWAY] {method} {url} -> {service_name} "
        f"[{status_code}] in {duration_ms}ms"
    )
