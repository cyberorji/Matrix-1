# Matrix-1

**Matrix-1**, yalnızca açık profil URL'leri üzerinden kullanıcı adı varlığını kontrol eden, terminal tabanlı ve izinli kullanım için tasarlanmış bir OSINT yardımcı aracıdır. Web arayüzü, hesap girişi, şifre, API anahtarı, CAPTCHA aşma veya proxy rotasyonu içermez.

> **Güvenli varsayılan:** Depoda 500 harici platform kaydı bulunur. Bu kayıtlar katalogda kapalıdır ve varsayılan çalıştırmada sorgulanmaz. Harici katalog açıkça `--include-external` ile seçilmeden yüzlerce üçüncü taraf platforma istek gönderilmez.

## Neler değişti?

- 500 harici platform kaydı, kaynak ve lisans bilgileriyle eklendi.
- Harici kayıtlar varsayılan olarak kapalı tutuldu.
- HTTP durum kodu tek başına yeterli kabul edilmiyor; katalogdaki bulunan/bulunmayan işaretleri de kontrol ediliyor.
- `found`, `not_found`, `unknown`, `blocked`, `rate_limited`, `server_error` ve `network_error` durumları ayrıştırılıyor.
- Kontrollü eşzamanlılık, timeout ve istek öncesi bekleme desteği geldi.
- JSON, NDJSON, CSV ve TXT çıktı biçimleri destekleniyor.
- Kategori filtresi, platform listeleme ve tüm durumları dışa aktarma seçenekleri eklendi.
- Katalog kayıtları URL, alan, tekrar ve HTTP kodu açısından doğrulanıyor.

## Kurulum

### Termux

```sh
pkg update -y && pkg install -y python git && git clone https://github.com/cyberorji/Matrix-1.git && cd Matrix-1 && python -m venv .venv && . .venv/bin/activate && pip install -e .
```

### Linux

```sh
sudo apt update && sudo apt install -y python3 python3-venv git
git clone https://github.com/cyberorji/Matrix-1.git
cd Matrix-1
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

### Windows

```powershell
git clone https://github.com/cyberorji/Matrix-1.git
cd Matrix-1
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e .
```

## Kullanım

Güvenli varsayılan mod yalnızca Matrix-1 tarafından açıkça etkinleştirilmiş kayıtları kullanır:

```sh
python run_matrix1.py cybermatrix --mode multi --limit 100 --out results.json --format json
```

Harici kaynak kataloğundaki 500 kaydı kullanmak için bunu açıkça belirtin. İlk denemelerde düşük limit ve düşük eşzamanlılık kullanın:

```sh
python run_matrix1.py cybermatrix --include-external --limit 25 --workers 2 --delay 1 --all-results --out results.ndjson --format ndjson
```

Kullanıcı adı verilmezse terminalde sorulur:

```sh
matrix1
```

Yalnızca bir kategori:

```sh
matrix1 cybermatrix --include-external --category developer --limit 50
```

Etkin kayıtları listeleme:

```sh
matrix1 --include-external --list-platforms
```

Desteklenen seçenekler:

- `--mode single|multi`: tek platform veya katalog sınırı.
- `--limit N`: kontrol edilecek en fazla kayıt sayısı.
- `--include-external`: kaynak kataloğundaki kapalı kayıtları açıkça dahil eder.
- `--all-results`: yalnızca bulunanları değil, belirsiz ve hatalı sonuçları da yazar.
- `--workers 1..16`: kontrollü eşzamanlı istek sayısı; varsayılan 4.
- `--delay SECONDS`: her istek öncesi bekleme.
- `--timeout SECONDS`: tek istek için zaman aşımı.
- `--format json|ndjson|csv|txt`: çıktı biçimi.

## Sonuçların anlamı

- `found`: bulunan işareti doğrulandı.
- `not_found`: bulunamadı işareti veya HTTP 404 doğrulandı.
- `unknown`: sunucu yanıtı kesin karar vermeye yetmedi.
- `blocked`: 401/403 gibi erişim kısıtı.
- `rate_limited`: HTTP 429.
- `server_error`: HTTP 5xx.
- `network_error`: timeout, DNS veya bağlantı hatası.

Bir platformun `200 OK` döndürmesi tek başına hesabın bulunduğunu kanıtlamaz. Bu yüzden sonuçlarda `unknown` durumu korunur ve kullanıcıya yanlış kesinlik verilmez.

## Katalog ve kaynak

`data/platforms.json` içindeki her kayıt `name`, `url_template`, `enabled`, `official`, `category` ve isteğe bağlı `detection` alanlarını taşıyabilir. Harici 500 kayıt, [WhatsMyName](https://github.com/WebBreacher/WhatsMyName) projesinin `wmn-data.json` verisinden dönüştürülmüştür. Bu veri CC BY-SA 4.0 lisanslıdır; Matrix-1 bu kaynağı taklit etmez veya resmi olarak temsil etmez.

Harici platformlar için `enabled=false` ve `official=false` kullanılır. Bu ayrım, yeni kayıtların yanlışlıkla varsayılan taramaya girmesini önler. Platformların URL'leri ve tespit işaretleri zamanla değişebilir; sonuçlar kesin kimlik doğrulaması değildir.

## Test

```sh
python -m pip install -e '.[test]'
python -m pytest -q
```

## Sorumlu kullanım

Yalnızca kendinize ait hesapları veya açıkça izin aldığınız kullanıcı adlarını kontrol edin. Platformların kullanım şartlarına, rate-limit kurallarına ve bulunduğunuz yerdeki yasalara uyun. CAPTCHA aşma, proxy rotasyonu, kimlik doğrulama atlatma ve gizli API kullanımı bu projeye dahil değildir. Sonuç dosyaları sorgulanan kullanıcı adlarını içerebilir; bunları paylaşmadan önce dikkat edin.

## Lisans

MIT. Harici WhatsMyName veri kayıtları ayrıca CC BY-SA 4.0 lisansına tabidir. Bu lisanslar platformların kullanım şartlarını veya yürürlükteki yasaları geçersiz kılmaz.
