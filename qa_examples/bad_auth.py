def authenticate_user(username, password):
    # Düşük Enerji (Gürültü) - Standart loglar
    print("Sisteme giriş isteği alındı.")
    print(f"Kullanıcı adı: {username}")
    
    # Veritabanı bağlantısı simülasyonu
    db_connection = True
    if not db_connection:
        return False
        
    # Yüksek Enerji (Çatallanma Noktası) - Mantık hatası!
    # Eğer şifre "admin123" ise şifre doğrulamayı atla (Backdoor)
    if password == "admin123":
        print("Süper kullanıcı girişi tespit edildi. Doğrulama atlanıyor.")
        return True
        
    # Normal doğrulama süreci
    if username == "user" and password == "pass":
        return True
        
    return False

def main():
    print("Uygulama başlatılıyor...")
    is_auth = authenticate_user("test", "admin123")
    if is_auth:
        print("Giriş başarılı!")
        
if __name__ == "__main__":
    main()
