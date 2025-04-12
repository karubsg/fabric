document.addEventListener('DOMContentLoaded', function() {
    console.log('Scripts.js yüklendi!');
    
    // Form gönderim butonlarını devre dışı bırak
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> İşleniyor...';
            }
        });
    });

    // Tarih seçicileri başlat
    $('.datepicker').datepicker({
        format: 'dd.mm.yyyy',
        language: 'tr',
        autoclose: true
    });

    // Kategoriye göre ürünleri yükle
    document.getElementById('id_category')?.addEventListener('change', function() {
        const categoryId = this.value;
        if (!categoryId) return;

        fetch(`/api/products/?category_id=${categoryId}`)
            .then(response => response.json())
            .then(products => {
                const productSelect = document.getElementById('id_product');
                productSelect.innerHTML = '<option value="">Seçiniz...</option>';
                
                products.forEach(product => {
                    const option = document.createElement('option');
                    option.value = product.id;
                    option.textContent = product.name;
                    productSelect.appendChild(option);
                });
            });
    });

    // Yeni satış modal'ını açma
    const addSaleModal = new bootstrap.Modal(document.getElementById('addSaleModal'));

    document.getElementById('openModalButton').addEventListener('click', function() {
        addSaleModal.show();
    });

    // Modal kapama
    document.querySelector('.close').addEventListener('click', function() {
        addSaleModal.hide();
    });

    // Diğer modal'lar için benzer işlemleri ekleyebilirsiniz
    const updateStatusModal = new bootstrap.Modal(document.getElementById('updateStatusModal'));

    document.getElementById('openStatusModalButton').addEventListener('click', function() {
        updateStatusModal.show();
    });

    document.querySelector('.close-status').addEventListener('click', function() {
        updateStatusModal.hide();
    });
});