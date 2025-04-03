# Raccolta Differenziata per Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Un'integrazione per Home Assistant che ti aiuta a gestire la raccolta differenziata, con notifiche e visualizzazione dei prossimi conferimenti.

## Funzionalità

- Gestione dei conferimenti su base settimanale, bisettimanale o mensile
- Notifiche push tramite l'applicazione Companion di Home Assistant
- Supporto multilingua (italiano e inglese)
- Card Lovelace personalizzata per visualizzare:
  - Il prossimo conferimento
  - I due conferimenti successivi con indicazione del giorno

## Installazione

### HACS (consigliato)

1. Assicurati di avere [HACS](https://hacs.xyz/) installato
2. Vai su HACS > Integrazioni > Menu (in alto a destra) > Archivi personalizzati
3. Aggiungi `https://github.com/nitbooz/ha-raccolta-differenziata` come repository personalizzato (categoria: Integrazione)
4. Cerca "Raccolta Differenziata per HA" nelle integrazioni HACS e installala
5. Riavvia Home Assistant

### Manuale

1. Scarica l'ultima versione da [GitHub](https://github.com/nitbooz/ha-raccolta-differenziata)
2. Estrai il contenuto nella cartella `/config/custom_components/raccolta_differenziata` di Home Assistant
3. Riavvia Home Assistant

## Configurazione

Aggiungi la seguente configurazione al tuo file `configuration.yaml`:

```yaml
raccolta_differenziata:
  conferimenti:
    - tipo: "Plastica"
      giorno: "lunedì"
      frequenza: "settimanale"
      colore: "#ffcc00"
      icona: "mdi:recycle"
    - tipo: "Carta"
      giorno: "mercoledì"
      frequenza: "bisettimanale"
      colore: "#0066cc"
      icona: "mdi:newspaper-variant-outline"
    # Aggiungi altri conferimenti secondo necessità
  notifiche:
    attive: true
    orario: "19:00"
    anticipo: 1  # giorni di anticipo per la notifica
```

## Utilizzo della Card Lovelace

Dopo l'installazione, puoi aggiungere la card personalizzata al tuo dashboard Lovelace:

1. Vai su "Panoramica" > "Modifica dashboard" > "Aggiungi card" > "Personalizzata: Raccolta Differenziata Card"
2. Configura la card secondo le tue preferenze

## Supporto

Per segnalare problemi o richiedere nuove funzionalità, apri una issue su [GitHub](https://github.com/nitbooz/ha-raccolta-differenziata/issues).

## Licenza

Questo progetto è rilasciato sotto licenza MIT.