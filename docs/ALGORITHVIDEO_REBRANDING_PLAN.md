> Historical rebranding plan, dated 2026-10-24. The temporary 0.2.0 working version was superseded by the fresh AlgorithVideo 0.1.0 Windows x64 edition. The proposed destinations, local-only scope and test results below describe that earlier stage, not current publication instructions. On 2026-10-25, MIT and the public source repository [algorithco/algorith-video](https://github.com/algorithco/algorith-video) were selected. See [source readiness](OPEN_SOURCE_READINESS.md) and [Windows packaging](RELEASING.md) for the current publication and binary-release requirements.

# AlgorithVideo: Algorithco brendiga to‘liq o‘tish rejasi (tarixiy)

Sana: 2026-10-24. Audit bazasi: `b996820`, `main`, package versiyasi `0.1.19`.
Ishchi loyiha: Algorithco’ning lokal checkout’i.
Holat: lokal rebrending bajarildi. Yakuniy natijalar [tekshiruv hisobotida](ALGORITHVIDEO_REBRANDING_VERIFICATION.md).

## 1. Maqsad va yangi identifikatsiya

Foydalanuvchi ko‘radigan barcha mahsulot nomlari, belgilar, ishlab chiqaruvchi ma’lumotlari, ichki mahsulot identifikatorlari va tarqatish paketlarini AlgorithVideo / Algorithco brendiga o‘tkazish.

| Qism | Yangi qiymat |
| --- | --- |
| Mahsulotning aniq nomi | `AlgorithVideo` |
| Ishlab chiqaruvchi | `Algorithco` |
| npm paketi va Linux executable | `algorithvideo` |
| Electron appId / Windows AppUserModelId | `com.algorithco.algorithvideo` — amalga oshirish uchun taklif |
| Asosiy logo manbasi | `resources/algorithvideo-logo-source.png` |
| UI’dagi ishlab chiqaruvchi satri | `Developed by Algorithco` |
| Yangi standart eksport papkasi | `~/AlgorithVideo` |
| Yangi preload API | `window.algorithvideo` / `AlgorithVideoAPI` |
| Yangi sozlama va muhit prefiksi | `algorithvideo.*` / `ALGORITHVIDEO_*` |
| Yangi o‘rnatish fayli | `AlgorithVideo-${version}-${os}-${arch}.${ext}` |

Yangi release reposi uchun `algorithco/algorithvideo` nomi taklif qilinadi; bu repo mavjudligi yoki release nashriga berilgan ruxsat deb hisoblanmaydi. Rasmiy sayt, support va release manzillari alohida konfiguratsiyada belgilanadi. Qo‘shni Algorithco saytida `https://trqsh.uz` va `hello@algorithco.com` uchraydi; AlgorithVideo uchun yakuniy manzillar deb avtomatik qabul qilinmaydi.

## 2. Auditda aniqlangan asosiy bog‘liqliklar

- Qidirilgan doirada eski brend taxminan 196 ta matn faylida uchraydi; lockfile va binary assetlar bundan tashqari tekshiriladi.
- `src/shared/brand.ts` nom va URL’larning bir qismini markazlashtiradi, lekin ko‘plab matnlar boshqa fayllarda alohida yozilgan.
- `package.json`, `electron-builder.yml`, HTML title, native menyu va Windows AppUserModelId eski identifikatsiyani ishlatadi.
- Sidebar va About oynasi uch xil assetdan foydalanadi: mahsulot logosi, app ikonkasi va kompaniya belgisi. Faqat bitta PNG’ni almashtirish yetarli emas.
- `src/preload/index.ts` rendererga `window.bridgeclip` API’sini beradi. AI vositalari va MCP serverida ham mahsulot nomi mavjud.
- `src/main/settings-store.ts` standart eksportni `~/BridgeClip` ichiga yozadi. Sidebar va Zernio profilida eski localStorage kalitlari, Library’da `.bridgeclip-favorite` va `.bridgeclip-posted-*` markerlari bor.
- Yangilanish manzili `src/main/update-provider.ts` va `electron-builder.yml` ichida eski repoga bog‘langan.
- macOS Team ID `9CBJCDR3J2`, Windows publisher `BRIDGEMIND LLC` va release tekshiruvlari avvalgi ishlab chiqaruvchiga tegishli.
- `scripts/icon/build-icons.sh` macOS’dagi `sips` / `iconutil` vositalariga bog‘langan. Windows’dan qayta eksport qilish usuli ham kerak.
- README’dan tashqari changelog, hujjatlar, test fixture’lari, release scriptlari va social rasmlarida ham eski brend mavjud.

## 3. Birinchi bosqich: qayta ishlash uchun boshlang‘ich holat

1. Toza checkout va hozirgi commitni qayd etish; o‘zgarishlarni alohida lokal branchda yuritish.
2. `npm ci`, Python 3.12 virtual muhiti va hash bilan tekshiriladigan `engine/requirements.lock` orqali dependency’larni o‘rnatish.
3. Node.js 22, Python, yt-dlp va subtitr filtri mavjud FFmpeg’ni tekshirish.
4. Typecheck, lint, asosiy testlar, Python engine testlari va production buildning boshlang‘ich natijasini qayd etish. Oldindan mavjud xatolarni yangi o‘zgarishlar keltirib chiqargan xatolardan ajratish.
5. Eski nomlarning yozilish variantlari, eski URL, appId, sertifikat identifikatorlari va assetlar uchun inventar yaratish.

Natija: o‘zgarishlardan oldingi holat va keyingi tekshiruvlarga solishtirish bazasi.

## 4. Ikkinchi bosqich: nom va ishlab chiqaruvchini almashtirish

1. `src/shared/brand.ts` ni mahsulot nomi, ishlab chiqaruvchi, tagline, sayt, support, repo va release konfiguratsiyasining asosiy manbasiga aylantirish.
2. `package.json` va `package-lock.json` dagi root metadata’ni birga yangilash; birinchi AlgorithVideo versiyasini changelog va package ma’lumotlari bilan mos belgilash.
3. `electron-builder.yml`, native oynalar, menyular, HTML title, About, onboarding, xatolik matnlari, eksport holatlari va accessibility matnlarini yangilash.
4. `BridgeClipLogo` komponentini `AlgorithVideoLogo` qilib nomlash va barcha importlarni o‘zgartirish.
5. `BRIDGEMIND_URL` kabi kompaniya nomiga bog‘langan konstantalarni `COMPANY_URL` kabi umumiy nomlarga o‘tkazish; tashqi havolalar allowlistini yangilash.
6. OpenRouter `X-Title`, `HTTP-Referer`, User-Agent va foydalanuvchiga yuboriladigan mahsulot metadata’sini yangilash.
7. AI assistant system prompti, tool tavsiflari, bildirishnomalar, misollar va yordam matnlarini yangi nomga moslashtirish.

Natija: foydalanuvchi interfeysida mahsulot `AlgorithVideo`, ishlab chiqaruvchi `Algorithco` sifatida ko‘rinadi.

## 5. Uchinchi bosqich: yangi logo va vizual uslub

Berilgan manba: 1254 × 1254 px, RGB PNG, qora fon; alpha shaffofligi mavjud emas. Belgida oq geometrik ramka va sariq play uchburchagi bor.

1. Original faylni yo‘qotmasdan repo ichida `resources/algorithvideo-logo-source.png` sifatida saqlash.
2. Shu belgidan app icon, ixcham mark va `AlgorithVideo` yozuvli lockup variantlarini tayyorlash. Nom doimo aynan shu registrda yoziladi.
3. Sidebar, tor sidebar, Settings/About, loading holati, taskbar/dock va installer uchun assetlarni ulash.
4. Qora/oq asos va sariq urg‘uni dizayn tokenlarida belgilash; sariq primary tugmalarda o‘qilishi yaxshi qora matn ishlatish. Xato, ogohlantirish va muvaffaqiyat ranglari alohida ma’noga ega bo‘ladi.
5. PNG, Windows uchun ko‘p o‘lchamli ICO, macOS uchun ICNS hamda Linux ikonkasini eksport qilish. Ixcham belgi 16, 24 va 32 px’da ham tekshiriladi.
6. Katta originaldagi bo‘sh joyning kichik ikonkalarga ta’sirini tekshirish; belgi geometriyasi saqlangan holda optik masshtabni moslash.
7. Qora fonli manbadan shaffof yoki yorug‘ fonli variant chiqarilsa, uni alohida hosila asset sifatida tayyorlash va oq ramka kontrastini tekshirish.
8. Eksport vositalarini Windows va CI’da qayta bajarish mumkin qilish; macOS paketini native macOS’da tekshirish.
9. Eski SVG/PNG logolar, ichiga PNG joylangan SVG’lar, bannerlar va qo‘llanmadagi screenshotlarni ham yangilash. Matn qidiruvi rasmlar ichidagi eski nomlarni topmasligi hisobga olinadi.
10. `DESIGN.md`, icon qo‘llanmasi va asset manbalari haqidagi yozuvlarni yangi dizaynga moslash.

Natija: taqdim etilgan logo barcha platforma va ilova holatlarida bir xil mahsulotni ifodalaydi.

## 6. To‘rtinchi bosqich: ichki identifikatorlar va eski ma’lumotlar

1. `BridgeClipAPI` / `window.bridgeclip` dan `AlgorithVideoAPI` / `window.algorithvideo` ga preload, renderer, type declaration va mocklarda birgalikda o‘tish.
2. MCP server nomi, token environment kaliti, `show_in_bridgeclip` kabi tool nomlari, CLI markerlari va tegishli testlarni moslashtirish.
3. `BRIDGECLIP_*` environment o‘zgaruvchilari va Python’dagi mahsulot prefiksli konfiguratsiyalarni yangilash; desktop orqali ishlatiladiganlarini ham, qolgan konfiguratsiyalarni ham qidiruvga kiritish.
4. Yangi foydalanuvchi ma’lumotlari va eksportlari uchun AlgorithVideo nomli yo‘llarni joriy qilish. Oldindan tanlangan custom output papkalari avtomatik qayta nomlanmaydi.
5. Eski o‘rnatishdan import kerak bo‘lsa, uni alohida migratsiya oqimi orqali bajarish: avval backup, keyin nusxa, natijani tekshirish va takror ishga tushganda dublikat yaratmaslik.
6. OS secure storage’dagi kalitlarning boshqa app identifikatsiyasida ochilishi kafolatlanmaydi. Shunday holatda API kalitini qayta kiritish oqimini ishlatish; credentiallarni ochiq ko‘rinishda ko‘chirmaslik.
7. Library markerlari, localStorage kalitlari, job tarixi, bookmarklar va posted status uchun moslik qoidalarini belgilash.
8. Eski nomlar faqat aniq belgilangan migratsiya qatlamida va uning fixture/testlarida qolishi mumkin. Yangi yozuvlar yangi nomlardan foydalanadi.

Natija: renderer, Electron va Python o‘rtasidagi shartnomalar birga yangilanadi; mavjud kutubxonani import qilish imkoniyati tekshiriladi.

## 7. Beshinchi bosqich: build, installer va yangilanishlar

Bu qismda repo nomini oddiy almashtirishning o‘zi yetarli emas: tarqatish manbasi va imzolovchi ham yangi ishlab chiqaruvchiga mos bo‘lishi kerak.

1. Windows Start menu, shortcut, taskbar, installer, uninstaller, ProductName va executable nomlarini `AlgorithVideo` ga o‘tkazish.
2. macOS bundle/display nomi, appId, DMG va ZIP nomlari; Linux executable, DEB/AppImage metadata’sini yangilash.
3. `electron-builder.yml`, `src/main/update-provider.ts`, release manifestlari va tekshiruv scriptlarini bitta release konfiguratsiyasiga moslashtirish.
4. AlgorithVideo release manbasi mavjud va tekshirilgan bo‘lguncha eski BridgeClip update feediga so‘rov yuborishni to‘xtatish; holat UI’da tushunarli ko‘rsatiladi.
5. Algorithco’ning haqiqiy code-signing ma’lumotlari bilan Windows publisher va macOS Team ID ni sozlash. Sertifikatdagi yuridik nomni taxminiy `Algorithco LLC` bilan almashtirmaslik.
6. Eski ishlab chiqaruvchining signing identity’si yoki public key’idan yangi rasmiy relizni tasdiqlash uchun foydalanmaslik. Repo ichidagi release kalitlari va ulardan foydalanadigan jarayonlarni inventar asosida yangilash.
7. Yangi installerning o‘rnatilishi, ochilishi, olib tashlanishi va versiya metadata’sini tekshirish. Imzo tekshiruvlari saqlanadi.
8. Rasmiy yangilanish tayyor bo‘lganda, AlgorithVideo’ning ikki test versiyasi o‘rtasida haqiqiy upgrade sinovini bajarish. Har platforma holatini o‘sha platformada tekshirish.

Natija: paketlar AlgorithVideo nomida chiqadi va faqat uning o‘z relizlarini yangilanish deb qabul qiladi.

## 8. Oltinchi bosqich: hujjatlar, repo va attribution

1. README, development/usage/editor/assistant/privacy/releasing qo‘llanmalari, changelogning yangi mahsulotga oid qismlari, `.env.example`, SECURITY va contribution matnlarini yangilash.
2. `.github` issue/PR template’lari, CODEOWNERS, eski maintainer aloqalari, release qo‘llanmalari va public-draft manifestini moslashtirish.
3. Eski mahsulot screenshotlari va social bannerlarini almashtirish; tarixiy release yozuvlarini kelib chiqishi ko‘rsatilgan hujjat sifatida ajratish yoki yangi mahsulot tarixidan chiqarish.
4. Yangi rasmiy repo tayyor bo‘lganda uni `origin`, original repozitoriyni esa manba sifatida `upstream` qilib belgilash. Git tarixini qayta yozmaslik.
5. Mahsulot matnlarida ishlab chiqaruvchini Algorithco deb ko‘rsatish. Original kodning MIT copyright/permission matnlarini `LICENSE`, `engine/LICENSE` va tegishli notices’da saqlash; Algorithco’ning qo‘shimcha ishlariga tegishli attributionni aniq ajratish.
6. FFmpeg, Python, fontlar, YuNet va boshqa bog‘liqliklarning mavjud litsenziya yozuvlarini paketda saqlash.

MIT matni copyright va permission notice’ni saqlash shartini o‘z ichiga oladi: [Open Source Initiative: MIT](https://opensource.org/license/mit). Shu sabab eski nomlarning litsenziya yozuvlarida uchrashi mahsulot rebrendingidan alohida nazorat qilinadi.

Natija: yangi mahsulot hujjatlari AlgorithVideo / Algorithco nomida, manba va dependency notices’lari aniq.

## 9. Yettinchi bosqich: tekshiruv va qabul mezonlari

### Avtomatik tekshiruvlar

- `npm run typecheck`
- `npm run lint`
- `npm test`
- `npm run build`
- Python engine testlari: Windows’da `engine/.venv/Scripts/python.exe -m pytest -q engine/tests`.
- Tegishli E2E oqimlari; testlar haqiqiy foydalanuvchi profili va chiqish papkasidan izolyatsiya qilinadi.
- Rebrendingni qayta buzmaslik uchun inventar tekshiruvi: eski product/kompaniya nomlari, URL’lar, appId, imzo identifikatorlari va asset fayllariga kutilmagan yangi havola yo‘q.
- Avvalgi nomlar uchun faqat litsenziya/kelib chiqish, aniq legacy migratsiya va tegishli fixture’lardan iborat tor ro‘yxat ruxsat etiladi. `.git` qidiruv doirasiga kirmaydi.

### Amaliy tekshiruvlar

1. Ilova ochilishi, onboarding, Sidebar, Chat, Jobs, Library, Settings/About, menyu va xatolik oynalari.
2. Lokal video bilan import → kesish → subtitr → preview → tahrirlash → eksport oqimi.
3. YouTube manbasi va OpenRouter’li kichik real job, mavjud API kaliti va provider xarajatlari doirasida.
4. Eski kutubxonadan import va yangi toza profil holatlari; kalitlarni qayta kiritish ssenariysi.
5. AI tool chaqiruvlari va tasdiqlash kartalarida yangi nom; tashqi havolalar allowlisti.
6. Windows installer/shortcut/taskbar/uninstaller; boshqa OS paketlari o‘z platformalarida.
7. Kichik ikonkalarda, tor sidebarda va About oynasida logoning tiniqligi, kesilmasligi va kontrasti.
8. Zernio uchun hisob ulash va post oqimlarini mock/sinov muhitida tekshirish; real ommaviy post alohida foydalanuvchi topshirig‘i bilan bajariladi.

### Ish tugagan deb hisoblash

- Foydalanuvchi ko‘radigan barcha o‘rinlarda `AlgorithVideo` va `Algorithco` mavjud.
- Taqdim etilgan yangi logo eski mahsulot va kompaniya belgilarining o‘rnini egallagan.
- Yangi ma’lumotlar, API nomlari va installerlar yangi identifikatorlardan foydalanadi.
- Eski update repoga so‘rov yo‘q; Algorithco reliz konfiguratsiyasi yoqilmagan bo‘lsa, yangilanish o‘chiq holatda aniq ko‘rsatiladi.
- Testlar va build natijalari qayd etilgan, tekshirilmagan platforma yoki oqimlar aniq yozilgan.
- Litsenziya va kelib chiqish notices’lari saqlangan; kutilmagan eski nom/asset qolmagan.

## 10. Tavsiya etilgan bajarish tartibi va tashqi ma’lumotlar

Bajarish ketma-ketligi: boshlang‘ich tekshiruv → nom va metadata → yangi logo/UI → ichki identifikatorlar va migratsiya → installer/updater → hujjatlar → to‘liq tekshiruv.

Repo/release manzillari, rasmiy support sayti yoki code-signing sertifikatlari aniqlanmagan paytda ham lokal rebrending, assetlar, ichki nomlash, testlar va lokal build bajarilishi mumkin. Rasmiy tarqatishni yoqish uchun quyidagilar kerak bo‘ladi:

- AlgorithVideo’ning yakuniy GitHub repo/release manzili.
- Kompaniya sayti va support/issue manzillari.
- Imzolangan reliz talab qilinadigan platformalar uchun Algorithco’ning amaldagi signing ma’lumotlari.
- Birinchi AlgorithVideo reliz versiyasi va native platformalarda tekshirish imkoniyati.

Bu hujjatni tayyorlash jarayonida dastur kodi, logotip assetlari, Git remote yoki o‘rnatilgan foydalanuvchi ma’lumotlari o‘zgartirilmagan.

## 11. Lokal amalga oshirish yakuni

Foydalanuvchi repo va sayt mavjud emasligini, faqat lokal ishlar bajarilishini belgiladi. AlgorithVideo 0.2.0 nomi, Algorithco metadatasi, yangi logo/UI, ichki identifikatorlar, Library mosligi va lokal tarqatish konfiguratsiyasi tayyorlandi. Yangilanishlar va public mahsulot havolalari sozlanmagan holatda. Typecheck, lint, build, asosiy testlar, 1062 engine testi va 2 E2E sinovi o‘tdi; batafsil natija va cheklovlar [verification hujjatida](ALGORITHVIDEO_REBRANDING_VERIFICATION.md).
