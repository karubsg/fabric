// Ödeme işlemleri için JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Form elementi
    const form = document.querySelector('form');
    const dateInput = document.getElementById('id_date');
    const saleSelect = document.getElementById('id_sale');
    const amountInput = document.getElementById('id_amount');
    const submitButton = document.querySelector('button[type="submit"]');

    // Sayfa yüklendiğinde tarihi bugüne ayarla
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }

    // Form gönderildiğinde
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Kaydet butonunu devre dışı bırak ve yükleniyor göster
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Kaydediliyor...';
            }
            
            // Form verilerini al
            const formData = new FormData(form);
            
            // AJAX ile form verilerini gönder
            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Ödeme kaydedilemedi');
                    });
                }
                return response.json();
            })
            .then(data => {
                // Başarılı ise mesajı göster ve yönlendir
                alert(data.message || 'Ödeme başarıyla kaydedildi');
                window.location.href = data.redirect || '/payments/';
            })
            .catch(error => {
                console.error('Hata:', error);
                alert('Ödeme kaydedilirken bir hata oluştu: ' + error.message);
                
                // Hata durumunda butonu tekrar aktif et
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = '<i class="bi bi-save"></i> Kaydet';
                }
            });
        });
    }

    // Ödeme yapıldığında seçilen satışı listeden kaldır
    function updateSaleOptions() {
        // Eğer ödeme tutarı, kalan bakiyeye eşit veya büyükse, o satışı listeden kaldır
        const amountInput = document.getElementById('id_amount');
        const saleSelect = document.getElementById('id_sale');
        
        if (amountInput && saleSelect) {
            amountInput.addEventListener('input', function() {
                const selectedOption = saleSelect.options[saleSelect.selectedIndex];
                if (selectedOption) {
                    // Kalan bakiye bilgisini seçenek metninden çıkar
                    const optionText = selectedOption.text;
                    const remainingMatch = optionText.match(/Kalan: [^\d]*(\d+\.?\d*)/); 
                    
                    if (remainingMatch && remainingMatch[1]) {
                        const remainingAmount = parseFloat(remainingMatch[1]);
                        const paymentAmount = parseFloat(amountInput.value) || 0;
                        
                        // Eğer ödeme tutarı kalan bakiyeye eşit veya büyükse, satış tamamen ödenmiş olur
                        if (paymentAmount >= remainingAmount) {
                            // Kullanıcıya bilgi ver
                            const infoElement = document.createElement('div');
                            infoElement.className = 'alert alert-info mt-2';
                            infoElement.textContent = 'Bu ödeme ile satış tamamen ödenmiş olacak.';
                            infoElement.id = 'payment-info-alert';
                            
                            // Eğer daha önce bir bilgi mesajı eklenmemişse ekle
                            const existingInfo = amountInput.parentNode.querySelector('.alert');
                            if (!existingInfo) {
                                amountInput.parentNode.appendChild(infoElement);
                            }
                            
                            // Otomatik olarak kalan bakiyeyi tam olarak öde
                            if (paymentAmount > remainingAmount) {
                                amountInput.value = remainingAmount.toFixed(2);
                            }
                        } else {
                            // Bilgi mesajını kaldır
                            const existingInfo = amountInput.parentNode.querySelector('.alert');
                            if (existingInfo) {
                                existingInfo.remove();
                            }
                        }
                    }
                }
            });
            
            // Satış seçildiğinde kalan bakiyeyi otomatik olarak doldur
            saleSelect.addEventListener('change', function() {
                const selectedOption = saleSelect.options[saleSelect.selectedIndex];
                if (selectedOption) {
                    const optionText = selectedOption.text;
                    const remainingMatch = optionText.match(/Kalan: [^\d]*(\d+\.?\d*)/); 
                    
                    if (remainingMatch && remainingMatch[1]) {
                        const remainingAmount = parseFloat(remainingMatch[1]);
                        // Kalan bakiyeyi ödeme tutarı olarak ayarla
                        amountInput.value = remainingAmount.toFixed(2);
                        
                        // Bilgi mesajını ekle
                        const infoElement = document.createElement('div');
                        infoElement.className = 'alert alert-info mt-2';
                        infoElement.textContent = 'Bu ödeme ile satış tamamen ödenmiş olacak.';
                        infoElement.id = 'payment-info-alert';
                        
                        // Eğer daha önce bir bilgi mesajı eklenmemişse ekle
                        const existingInfo = amountInput.parentNode.querySelector('.alert');
                        if (!existingInfo) {
                            amountInput.parentNode.appendChild(infoElement);
                        }
                    }
                }
            });
        }
    }
    
    // Sayfa yüklendiğinde satış seçeneklerini güncelle
    updateSaleOptions();
});