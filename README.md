# Matrix-1

**Matrix-1**, yalnızca izinli ve açıkça tanımlanmış platformlarda kullanıcı adı varlığını kontrol etmek için hazırlanmış güvenli bir OSINT yardımcı aracıdır. Cyber Matrix temalı web arayüzü; tekli/çoklu sorgu, yalnızca aktif doğrulanmış sonuçlar ve TXT/JSON dışa aktarma sunar.

> **Önemli:** Bu proje 30.000 siteyi agresif biçimde taramaz ve taramayı otomatik olarak genişletmez. “30.000 platform” hedefi, yalnızca yöneticinin izin verdiği katalog kayıtlarını tutan genişletilebilir şemadır. CAPTCHA aşma, proxy rotasyonu, rate-limit atlatma, gizli API kullanımı ve izinsiz hesap keşfi yoktur. Platformların şartlarına ve yerel yasalara uyun.

## Termux kurulumu (tek komut)

```sh
pkg update -y && pkg install -y python git && git clone https://github.com/cyberorji/Matrix-1.git && cd Matrix-1 && python -m venv .venv && . .venv/bin/activate && pip install -e .
```

## Linux kurulumu

```sh
sudo apt update && sudo apt install -y python3 python3-venv git
 git clone https://github.com/cyberorji/Matrix-1.git
 cd Matrix-1
 python3 -m venv .venv
 . .venv/bin/activate
 pip install -e .
```

## Windows kurulumu

PowerShell'i açın:

```powershell
git clone https://github.com/cyberorji/Matrix-1.git
cd Matrix-1
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e .
```

## CLI kullanımı

```sh
matrix1 cybermatrix --limit 100 --out results.json --format json
matrix1 cybermatrix --limit 100 --out results.txt --format txt
```

CLI, `data/platforms.json` içindeki `enabled=true` ve `official=true` kayıtları alır. Sonuç listesine yalnızca HTTP olarak doğrulanabilen aktif sonuçlar eklenir; ağ hataları ve pasif sonuçlar gösterilmez.

## Arayüz

`web/index.html` dosyasını yerel bir statik sunucuyla açabilirsiniz:

```sh
python3 -m http.server 8080 --directory web
```

Ardından `http://127.0.0.1:8080` adresini açın. Tarayıcı CORS veya platform politikaları nedeniyle HEAD isteklerini engelleyebilir; bu durumda CLI kullanın. Arayüz, sonuçları otomatik olarak seçtiğiniz TXT/JSON biçiminde indirir.

## Katalog genişletme

Her kayıt şu alanları taşımalıdır: `name`, `url_template`, `enabled`, `official`, `category`. Sadece açıkça izin verilen ve doğrulama yöntemi platformun şartlarına uygun olan kayıtları ekleyin. Yanlış pozitifleri azaltmak için yalnızca HTTP 200'ü hesap kanıtı saymayın; mümkünse resmî API adaptörü kullanın.

## Test

```sh
python -m pytest -q
```

## Lisans

MIT. Bu lisans, platform şartlarını veya yürürlükteki yasaları geçersiz kılmaz.
