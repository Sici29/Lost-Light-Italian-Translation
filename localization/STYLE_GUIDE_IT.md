# Guida di stile — versione 0.2
Master in radice obbligatorio. Italiano per Italia. Scelte di progetto, nessun canone ufficiale italiano attestato.
UI: imperativo singolare per istruzioni; nomi per intestazioni e stati. Tutorial: tu, naturale e diretto; genere del destinatario non dedotto. Dialoghi: voci dei personaggi solo dopo ricostruzione della scena.
Maiuscole/minuscole secondo il testo inglese dello stesso ID/contesto: preservare TUTTO MAIUSCOLO, Title Case e nomi di etichette/componenti, adattandoli alla struttura italiana senza normalizzazione automatica. Esempio: Equip a Receiver → Equipaggia un Castello (componente delle armi). Nomi armi, modelli, Jason e Heidi mantenuti; BAF conservato come nelle versioni ufficiali.
Distinguere Clicca, Tocca e Tieni premuto: il corpus contiene istruzioni condivise con mobile; non convertirle senza verificare il ramo PC.
PV per punti vita, zona di esclusione e punto di evacuazione. Banco di modifica distinto da banco da lavoro. Glossario 0.1; termini provvisori non propagabili automaticamente.
Encoding UTF-8 nei file di lavoro, LF nel JSONL. Apostrofo semplice, accenti italiani corretti, tre puntini per le sospensioni del campione. Nessuna modifica dei token o dei codici colore #RRGGBB; nessun riordino di placeholder impliciti.
No schwa/asterischi o maschile arbitrario: preferire riformulazioni naturali. Risate/interiezioni adattate secondo funzione, non sostituite con didascalie. Nomi, numeri e condizioni di gameplay preservati.
Bozze dubbie in drafts_pending.jsonl e campo it_draft; non incluse nei testi reviewed_static. Reviewed_static indica revisione dello stesso assistente, non test nel gioco né approvazione umana.

## Priorità linguistiche — istruzioni dell’utente
Spagnolo ufficiale come riferimento principale della traduzione e per genere/numero/pronomi/registro. L'inglese governa lo stile di maiuscole/minuscole. Per dubbi semantici o grammaticali consultare l'originale documentato e correggere eventuali discrepanze delle localizzazioni.
Lost Light: testi cinesi recuperati e collegati agli ID tramite MD5; consultarli per i dubbi quando disponibili. Questa evidenza non certifica automaticamente la lingua autoriale di ogni risorsa. Non presumere coreano o cinese senza provenienza.
Spagnolo mancante: indicare fallback alla sorgente recuperata o altra versione ufficiale; preservare tutte le lingue parallele disponibili. Genere degli oggetti secondo il sostantivo italiano, genere dei personaggi secondo il contesto, mai per trasferimento cieco dallo spagnolo.
Il lotto 001 precede queste direttive: non dichiararlo già revisionato rispetto alla guida 0.2. La maiuscola di Carcassa è stata corretta; audit complessivo da fare senza sostituzioni automatiche.

Test Impostazioni: stile inglese applicato alle etichette (es. Music and Sound → Musica e Suoni, Master Volume → Volume Generale). Spagnolo principale dove presente; altrimenti cinese del layout verificato per MD5. Le stringhe identiche in inglese ma diverse in cinese non autorizzano sostituzioni globali (Halo: alone grafico oppure anello di un oggetto).

Aggiornamento di stato: audit guida 0.2 delle 62 rese del lotto 001 completato in lotto 008. Dieci bozze ancora separate. Glossario 0.2 con termini tutorial adottati; nessun canone ufficiale italiano dichiarato. Gli speaker del tutorial rimangono da attribuire; il registro tu non prova una voce individuale.

## Direttive operative — Flusso Turbo (2026-10-11)
Turbo-batch da 200–240 unità per ciclo; pre-validazione automatica obbligatoria di parametri `{...}`, tag colore `#RRGGBB` e sequenza delle cifre numeriche; reporting aggregato delle metriche complessive (tradotte vs restanti); ricostruzione completa delle 18 tabelle binarie riservata ai traguardi milestone (ogni 1.000 unità); nessuna esecuzione dei binari di gioco.

## Receiver — consolidamento del 13 ottobre 2026
Per il componente delle armi usare Castello (maschile), coerentemente in etichette, descrizioni e missioni. Upper/Lower Receiver: Castello Superiore/Inferiore; Rail Receiver: Castello con Slitta; Receiver Rail: Slitta del Castello; Receiver Cover: Coperchio del Castello. Applicare le maiuscole dell’inglese della singola unità, mantenendo minuscole articoli e preposizioni italiane. Per dispositivi di comunicazione usare ricevitore, non Castello. Non sostituire alla cieca nomi, codici modello o varianti di uno stesso ID. Carcassa è una variante terminologica attestata, ma il progetto adotta Castello per coerenza; Ricevitore e Carrello non sono la resa adottata per 机匣. Fonte tecnica: manuale ufficiale Winchester Ranger, figura 23, pagina stampata 21 (Receiver / Castello). Audit per ID: analysis/Receiver_Terminology_126_Manual_Review.json; revisione statica, nessuna prova runtime implicita.

## Gradi militari — revisione del 13 ottobre 2026
Nel contesto military_data usare le categorie verificate sull’originale: 预备役: Riserva; 士兵: Soldato; 士官: Sottufficiale; 军士长: Sergente Maggiore; 尉官: Ufficiale Subalterno; 校官: Ufficiale Superiore; 将官: Generale; 五星上将: Generale dell’Esercito. Private in questo contesto è Soldato. L’inglese Officer accorpa categorie diverse: distinguere 士官 da 军士长 usando l’originale dell’ID. Conservare esattamente il glifo e il livello del numero romano della variante inglese (Ⅰ/Ⅱ/Ⅲ/Ⅳ/Ⅴ oppure I/II/III/IV/V): non normalizzare né sostituire con stelle o frecce. Rispettare la maiuscola inglese nella singola unità. Prova: analysis/Military_Rank_Source_Review_Candidates.json e military_rank_36_manual_review.json. Nessuna validazione runtime implicita.
