# Matrix-1

**Matrix-1**, yalnızca izinli ve açıkça tanımlanmış platformlarda kullanıcı adı varlığını kontrol eden **terminal tabanlı** güvenli bir OSINT yardımcı aracıdır. Web arayüzü yoktur; GitHub kullanıcı adı, GitHub şifresi, API anahtarı veya başka bir hesap bilgisi istemez.

> **Önemli:** Proje 30.000 siteyi agresif biçimde taramaz ve taramayı otomatik olarak genişletmez. 30.000 platform hedefi, yalnızca yöneticinin izin verdiği katalog kayıtlarını tutan genişletilebilir şemadır. CAPTCHA aşma, proxy rotasyonu, rate-limit atlatma, gizli API kullanımı ve izinsiz hesap keşfi yoktur.

## GitHub kimlik bilgisi neden isteniyordu?

Önceki depo `private` olduğu için `git clone` sırasında GitHub kimliği sorulabiliyordu. Bu sürümde depo **public** olarak yayımlanmıştır. Kurulum için GitHub kullanıcı adı, şifre veya token gerekmez. GitHub CLI ile giriş yapmanız da gerekmez.

## Termux kurulumu — tek komut

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

PowerShell'i açın. Bu komutlar GitHub hesabı istemez:

```powershell
git clone https://github.com/cyberorji/Matrix-1.git
cd Matrix-1
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e .
```

## Terminalde çalıştırma

Kullanıcı adını komutta verin:

```sh
matrix1 cybermatrix --mode multi --limit 100 --out results.json --format json
matrix1 cybermatrix --mode single --out results.txt --format txt
```

Kullanıcı adı verilmezse araç terminalde sorar:

```sh
matrix1
```

`--mode single` yalnızca ilk izinli platformu, `--mode multi` katalogdaki izinli platformları kontrol eder. `--limit` en fazla kaç platform kontrol edileceğini belirler. Sonuçlara yalnızca doğrulanabilen aktif kayıtlar eklenir; pasif veya ağ hatası olan kayıtlar yazdırılmaz.

## Katalog

`data/platforms.json` içindeki `enabled=true` ve `official=true` kayıtları kullanılır. Her kayıt `name`, `url_template`, `enabled`, `official` ve `category` alanlarını taşımalıdır. Kataloğa yalnızca kullanım izni olan platformları ekleyin.

## Test

```sh
python -m pytest -q
```

## Lisans

MIT. Bu lisans, platform şartlarını veya yürürlükteki yasaları geçersiz kılmaz.
