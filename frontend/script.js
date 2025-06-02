document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const dropArea = document.getElementById('dropArea');
    const fileInfo = document.getElementById('fileInfo');
    const processBtn = document.getElementById('processBtn');
    const btnText = document.getElementById('btnText');
    const spinner = document.getElementById('spinner');
    const previewSection = document.getElementById('previewSection');
    const previewTable = document.getElementById('previewTable').getElementsByTagName('tbody')[0];
    const downloadBtn = document.getElementById('downloadBtn');
    const tabs = document.getElementById('tabs');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const soldeInitialEl = document.getElementById('soldeInitial');
    const soldeFinalEl = document.getElementById('soldeFinal');
    const totalDebitsEl = document.getElementById('totalDebits');
    const totalCreditsEl = document.getElementById('totalCredits');
    
    let selectedFile = null;
    let jsonData = {
        compte_principal: [],
        agios: [],
        frais_commissions: []
    };
    let currentTab = 'compte';
    
    // Gestion du drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0 && files[0].type === 'application/pdf') {
            handleFiles(files);
        } else {
            fileInfo.textContent = 'Veuillez sélectionner un fichier PDF valide';
        }
    }
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFiles(fileInput.files);
        }
    });
    
    function handleFiles(files) {
        selectedFile = files[0];
        fileInfo.textContent = `Fichier sélectionné: ${selectedFile.name}`;
        processBtn.disabled = false;
    }
    
    // Traitement du fichier
    processBtn.addEventListener('click', async () => {
        if (!selectedFile) return;
        
        processBtn.disabled = true;
        btnText.textContent = 'Traitement en cours...';
        spinner.style.display = 'block';
        
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        try {
            // Étape 1: Upload et traitement du PDF
            const uploadResponse = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!uploadResponse.ok) {
                throw new Error('Échec du traitement du fichier');
            }
            
            const uploadData = await uploadResponse.json();
            
            if (uploadData.status === 'success') {
                // Étape 2: Récupérer les données pour l'aperçu
                const previewResponse = await fetch('/preview');
                
                if (!previewResponse.ok) {
                    throw new Error('Données de prévisualisation non disponibles');
                }
                
                jsonData = await previewResponse.json();
                
                // Afficher l'aperçu
                showPreview(jsonData.compte_principal);
                updateSummary(jsonData.compte_principal);
                tabs.style.display = 'flex';
                previewSection.style.display = 'block';
            } else {
                throw new Error(uploadData.message || 'Erreur lors du traitement du fichier');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Une erreur est survenue: ' + error.message);
        } finally {
            processBtn.disabled = false;
            btnText.textContent = 'Analyser le PDF';
            spinner.style.display = 'none';
        }
    });
    
    // Gestion des onglets
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTab = btn.dataset.tab;
            
            switch(currentTab) {
                case 'compte':
                    showPreview(jsonData.compte_principal);
                    updateSummary(jsonData.compte_principal);
                    break;
                case 'agios':
                    showPreview(jsonData.agios);
                    break;
                case 'frais':
                    showPreview(jsonData.frais_commissions);
                    break;
            }
        });
    });
    
    function showPreview(data) {
        previewTable.innerHTML = '';
        
        if (!Array.isArray(data)) {
            console.error('Invalid preview data:', data);
            return;
        }
        
        data.forEach(item => {
            // Vérifier si les deux champs débit et crédit sont vides ou nuls
            const debitEmpty = (item.debit === 0 || item.debit === undefined || item.debit === null);
            const creditEmpty = (item.credit === 0 || item.credit === undefined || item.credit === null);
            
            // Si les deux sont vides, on saute cette ligne
            if (debitEmpty && creditEmpty) {
                return; // équivalent à 'continue' dans une boucle forEach
            }
            
            const row = previewTable.insertRow();
            
            // Date
            const dateCell = row.insertCell(0);
            dateCell.textContent = item.date || '';
            
            // Libellé
            const libelleCell = row.insertCell(1);
            libelleCell.textContent = item.libelle || item.libellé || '';
            
            // Débit
            const debitCell = row.insertCell(2);
            if (!debitEmpty) {
                debitCell.textContent = item.debit.toFixed(2) + ' €';
                debitCell.classList.add('debit');
            }
            
            // Crédit
            const creditCell = row.insertCell(3);
            if (!creditEmpty) {
                creditCell.textContent = item.credit.toFixed(2) + ' €';
                creditCell.classList.add('credit');
            }
            
            // Type
            const typeCell = row.insertCell(4);
            typeCell.textContent = item.type || '';
        });
    }
    
    function updateSummary(data) {
        let soldeInitial = 0;
        let soldeFinal = 0;
        let totalDebits = 0;
        let totalCredits = 0;
        
        data.forEach(item => {
            if (item.type === 'solde_initial') {
                soldeInitial = item.credit;
            } else if (item.type === 'solde_final') {
                soldeFinal = item.credit;
            } else if (item.type === 'transaction') {
                totalDebits += item.debit || 0;
                totalCredits += item.credit || 0;
            }
        });
        
        soldeInitialEl.textContent = soldeInitial.toFixed(2) + ' €';
        soldeFinalEl.textContent = soldeFinal.toFixed(2) + ' €';
        totalDebitsEl.textContent = totalDebits.toFixed(2) + ' €';
        totalCreditsEl.textContent = totalCredits.toFixed(2) + ' €';
    }
    
    // Téléchargement du fichier Excel
    downloadBtn.addEventListener('click', () => {
        window.location.href = '/download';
    });
});