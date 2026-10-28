import json
from pathlib import Path
from matrix1.core import Platform, export_results, load_catalog, validate_username

def test_catalog_filters_disabled_and_unofficial(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps([
        {"name":"ok","url_template":"https://example.com/{username}","enabled":True,"official":True},
        {"name":"off","url_template":"https://example.com/{username}","enabled":False,"official":True},
        {"name":"unofficial","url_template":"https://example.com/{username}","enabled":True,"official":False}
    ]))
    assert [x.name for x in load_catalog(p)] == ["ok"]

def test_username_validation():
    assert validate_username("alice_01") == "alice_01"
    for value in ["", "a/b", "x" * 65]:
        try: validate_username(value)
        except ValueError: pass
        else: assert False

def test_export(tmp_path):
    results = [__import__('matrix1.core', fromlist=['Result']).Result('GitHub','alice','https://github.com/alice',True,'HTTP 200')]
    out = tmp_path / "r.txt"
    export_results(results, out, "txt")
    assert "GitHub" in out.read_text()
