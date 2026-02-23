import os
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_WDM = True
except ImportError:
    HAS_WDM = False

BASE_URL     = os.environ.get("BASE_URL", "http://localhost/DamnCRUD")
VALID_USER   = "admin"
VALID_PASS   = "nimda666!"
WAIT_TIMEOUT = 15
SS_DIR       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshoot")

os.makedirs(SS_DIR, exist_ok=True)


def get_driver():
    options = Options()
    # Use headless mode in CI/CD environments
    if os.environ.get("CI") or os.environ.get("HEADLESS"):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")

    if HAS_WDM:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(5)
    return driver


def take_screenshot(driver, tc_id, label):
    filename = f"{tc_id}_{label}.png"
    filepath = os.path.join(SS_DIR, filename)
    driver.save_screenshot(filepath)
    print(f"  [SS] Screenshot disimpan: screenshoot/{filename}")


def do_login(driver, username=VALID_USER, password=VALID_PASS):
    driver.get(f"{BASE_URL}/login.php")
    driver.find_element(By.ID, "inputUsername").clear()
    driver.find_element(By.ID, "inputUsername").send_keys(username)
    driver.find_element(By.ID, "inputPassword").clear()
    driver.find_element(By.ID, "inputPassword").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.url_contains("index.php"))


def search_in_datatable(driver, keyword):
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#employee_filter input"))
    )
    search_box = driver.find_element(By.CSS_SELECTOR, "#employee_filter input")
    search_box.clear()
    search_box.send_keys(keyword)
    time.sleep(1.5)


def get_total_entries(driver):
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#employee_info"))
    )
    time.sleep(1)
    info_text = driver.find_element(By.CSS_SELECTOR, "#employee_info").text
    try:
        return int(info_text.split(" of ")[1].split(" ")[0])
    except (IndexError, ValueError):
        return 0


class TC01_AksesTanpaLogin(unittest.TestCase):

    def setUp(self):
        self.driver = get_driver()

    def tearDown(self):
        self.driver.quit()

    def test_akses_tanpa_login(self):
        driver = self.driver

        print("\n  [TC01] Langkah 1-2: Navigasi ke index.php tanpa login...")
        driver.get(f"{BASE_URL}/index.php")
        time.sleep(1)

        print("  [TC01] Langkah 3-4: Verifikasi redirect dan ambil screenshot...")
        take_screenshot(driver, "TC01", "redirect_ke_login")

        self.assertIn("login.php", driver.current_url,
                      "FAIL: Seharusnya redirect ke login.php tanpa sesi aktif.")
        print("[TC01] PASS - Akses index.php tanpa login berhasil di-redirect ke login.php.")


class TC02_LihatDaftarKontak(unittest.TestCase):

    def setUp(self):
        self.driver = get_driver()

    def tearDown(self):
        self.driver.quit()

    def test_lihat_daftar_kontak(self):
        driver = self.driver

        print("\n  [TC02] Langkah 1-2: Login sebagai admin...")
        do_login(driver)

        print("  [TC02] Langkah 3: Menunggu tabel #employee muncul...")
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "employee"))
        )

        print("  [TC02] Langkah 4: Menghitung jumlah baris data...")
        rows = driver.find_elements(By.CSS_SELECTOR, "#employee tbody tr")

        print("  [TC02] Langkah 5: Ambil screenshot tabel kontak...")
        take_screenshot(driver, "TC02", "daftar_kontak_tampil")

        self.assertGreater(len(rows), 0,
                           "FAIL: Tabel kontak seharusnya memiliki minimal 1 baris data.")
        print(f"[TC02] PASS - Daftar kontak tampil dengan {len(rows)} baris data.")


class TC03_TambahKontakBaru(unittest.TestCase):

    NEW_NAME  = "Selenium Test User"
    NEW_EMAIL = "selenium@test.com"
    NEW_PHONE = "081234567890"
    NEW_TITLE = "QA Tester"

    def setUp(self):
        self.driver = get_driver()

    def tearDown(self):
        self.driver.quit()

    def test_tambah_kontak_baru(self):
        driver = self.driver

        print("\n  [TC03] Langkah 1: Login sebagai admin...")
        do_login(driver)

        print("  [TC03] Langkah 2-3: Navigasi ke form create dan tunggu input muncul...")
        driver.get(f"{BASE_URL}/create.php")
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "name"))
        )

        print("  [TC03] Langkah 4: Mengisi form dengan data kontak baru...")
        driver.find_element(By.ID, "name").send_keys(self.NEW_NAME)
        driver.find_element(By.ID, "email").send_keys(self.NEW_EMAIL)
        driver.find_element(By.ID, "phone").send_keys(self.NEW_PHONE)
        driver.find_element(By.ID, "title").send_keys(self.NEW_TITLE)

        print("  [TC03] Langkah 5: Screenshot form yang sudah terisi...")
        take_screenshot(driver, "TC03", "form_create_terisi")

        print("  [TC03] Langkah 6: Klik tombol Save...")
        submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        driver.execute_script("arguments[0].click();", submit_btn)

        print("  [TC03] Langkah 7: Menunggu redirect ke dashboard...")
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.url_contains("index.php"))
        self.assertIn("index.php", driver.current_url)

        print("  [TC03] Langkah 8: Mencari kontak baru via search box DataTable...")
        search_in_datatable(driver, self.NEW_NAME)

        print("  [TC03] Langkah 9-10: Screenshot hasil dan verifikasi kontak muncul...")
        take_screenshot(driver, "TC03", "create_kontak_berhasil")
        self.assertIn(self.NEW_NAME, driver.page_source,
                      f"FAIL: Kontak '{self.NEW_NAME}' tidak ditemukan setelah create.")
        print(f"[TC03] PASS - Kontak '{self.NEW_NAME}' berhasil ditambahkan dan tampil di dashboard.")


class TC04_UpdateKontak(unittest.TestCase):

    UPDATED_NAME  = "Updated Selenium User"
    UPDATED_EMAIL = "updated@selenium.com"
    UPDATED_TITLE = "Senior QA"

    def setUp(self):
        self.driver = get_driver()

    def tearDown(self):
        self.driver.quit()

    def test_update_kontak(self):
        driver = self.driver

        print("\n  [TC04] Langkah 1-2: Login dan tunggu tabel muncul...")
        do_login(driver)
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "employee"))
        )

        print("  [TC04] Langkah 3: Mengambil URL edit baris pertama...")
        edit_links = driver.find_elements(By.CSS_SELECTOR, "#employee tbody a.btn-success")
        self.assertGreater(len(edit_links), 0, "FAIL: Tidak ada tombol edit tersedia.")
        edit_url = edit_links[0].get_attribute("href")

        print(f"  [TC04] Langkah 4-5: Navigasi ke {edit_url}...")
        driver.get(edit_url)
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "name"))
        )

        print("  [TC04] Langkah 6: Mengubah data kontak...")
        name_field = driver.find_element(By.ID, "name")
        name_field.clear()
        name_field.send_keys(self.UPDATED_NAME)

        email_field = driver.find_element(By.ID, "email")
        email_field.clear()
        email_field.send_keys(self.UPDATED_EMAIL)

        title_field = driver.find_element(By.ID, "title")
        title_field.clear()
        title_field.send_keys(self.UPDATED_TITLE)

        print("  [TC04] Langkah 7: Screenshot form update yang terisi...")
        take_screenshot(driver, "TC04", "form_update_terisi")

        print("  [TC04] Langkah 8: Klik tombol Update...")
        submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        driver.execute_script("arguments[0].click();", submit_btn)

        print("  [TC04] Langkah 9: Menunggu redirect ke dashboard...")
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.url_contains("index.php"))
        self.assertIn("index.php", driver.current_url)

        print("  [TC04] Langkah 10: Mencari nama yang diupdate via DataTable search...")
        search_in_datatable(driver, self.UPDATED_NAME)

        print("  [TC04] Langkah 11: Verifikasi data baru tampil...")
        take_screenshot(driver, "TC04", "update_kontak_berhasil")
        self.assertIn(self.UPDATED_NAME, driver.page_source,
                      f"FAIL: Nama '{self.UPDATED_NAME}' tidak ditemukan setelah update.")
        print(f"[TC04] PASS - Kontak berhasil diupdate menjadi '{self.UPDATED_NAME}'.")


class TC05_HapusKontak(unittest.TestCase):

    def setUp(self):
        self.driver = get_driver()

    def tearDown(self):
        self.driver.quit()

    def test_hapus_kontak(self):
        driver = self.driver

        print("\n  [TC05] Langkah 1-2: Login dan tunggu tabel muncul...")
        do_login(driver)
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "employee"))
        )

        print("  [TC05] Langkah 3: Membaca total entries dari DataTable info...")
        total_before = get_total_entries(driver)
        self.assertGreater(total_before, 0, "FAIL: Tidak ada kontak yang bisa dihapus.")
        print(f"         Total entries sebelum hapus: {total_before}")

        print("  [TC05] Langkah 4: Mengambil URL delete baris terakhir...")
        rows = driver.find_elements(By.CSS_SELECTOR, "#employee tbody tr")
        last_row = rows[-1]
        contact_name = last_row.find_elements(By.TAG_NAME, "td")[1].text
        delete_btn = last_row.find_element(By.CSS_SELECTOR, "a.btn-danger")
        delete_url  = delete_btn.get_attribute("href")
        print(f"         Kontak yang akan dihapus: '{contact_name}'")

        print("  [TC05] Langkah 5: Screenshot sebelum hapus...")
        take_screenshot(driver, "TC05", "sebelum_hapus_kontak")

        print("  [TC05] Langkah 6: Navigasi ke URL delete (bypass confirm dialog)...")
        driver.execute_script(f"window.location.href = '{delete_url}';")

        print("  [TC05] Langkah 7-8: Menunggu redirect dan DataTable terupdate...")
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.url_contains("index.php"))
        time.sleep(1.5)

        print("  [TC05] Langkah 9: Membaca total entries setelah hapus...")
        total_after = get_total_entries(driver)
        print(f"         Total entries setelah hapus: {total_after}")

        print("  [TC05] Langkah 10-11: Screenshot dan verifikasi total berkurang...")
        take_screenshot(driver, "TC05", "hapus_kontak_berhasil")
        self.assertLess(total_after, total_before,
                        f"FAIL: Total seharusnya berkurang. Before={total_before}, After={total_after}")
        print(f"[TC05] PASS - Kontak '{contact_name}' berhasil dihapus. "
              f"Total: {total_before} -> {total_after}.")


if __name__ == "__main__":
    print("=" * 62)
    print("  DamnCRUD Functional Test Suite - 5 Test Cases (Soal No.4)")
    print(f"  Screenshots: {SS_DIR}")
    print("=" * 62)

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TC01_AksesTanpaLogin))
    suite.addTests(loader.loadTestsFromTestCase(TC02_LihatDaftarKontak))
    suite.addTests(loader.loadTestsFromTestCase(TC03_TambahKontakBaru))
    suite.addTests(loader.loadTestsFromTestCase(TC04_UpdateKontak))
    suite.addTests(loader.loadTestsFromTestCase(TC05_HapusKontak))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
