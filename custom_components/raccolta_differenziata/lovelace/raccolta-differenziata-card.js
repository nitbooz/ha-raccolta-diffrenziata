import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.4.0/lit-element.js?module';

class RaccoltaDifferenziataCard extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
    };
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 16px;
      }
      .card-header {
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 16px;
      }
      .collection {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
        padding: 12px;
        border-radius: 8px;
      }
      .collection-icon {
        margin-right: 16px;
        font-size: 2rem;
      }
      .collection-info {
        flex-grow: 1;
      }
      .collection-type {
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 4px;
      }
      .collection-date {
        font-size: 0.9rem;
        opacity: 0.8;
      }
      .days-until {
        font-size: 0.9rem;
        font-weight: 500;
        padding: 4px 8px;
        border-radius: 4px;
        background-color: var(--primary-color);
        color: var(--text-primary-color);
      }
    `;
  }

  constructor() {
    super();
    this._sensors = [];
  }

  setConfig(config) {
    if (!config) {
      throw new Error('Invalid configuration');
    }
    this.config = config;
  }

  getCardSize() {
    return 3;
  }

  render() {
    if (!this.hass || !this.config) {
      return html``;
    }

    // Trova i sensori dell'integrazione raccolta_differenziata
    this._findSensors();

    // Ottieni la lingua configurata in Home Assistant
    const language = this.hass.language || 'en';
    const translations = this._getTranslations(language);

    return html`
      <ha-card>
        <div class="card-header">
          ${this.config.title || translations.next_collection}
        </div>
        <div class="card-content">
          ${this._renderCollections(translations)}
        </div>
      </ha-card>
    `;
  }

  _findSensors() {
    this._sensors = [];
    const sensorTypes = ['next', 'next_plus_one', 'next_plus_two'];
    
    for (const sensorType of sensorTypes) {
      const entityId = `sensor.raccolta_differenziata_${sensorType}`;
      if (this.hass.states[entityId]) {
        this._sensors.push(entityId);
      }
    }
  }

  _renderCollections(translations) {
    if (!this._sensors.length) {
      return html`<div>No waste collection sensors found</div>`;
    }

    // Determina quanti conferimenti mostrare (default: 1)
    const showCount = this.config.show_count || 1;
    const sensorsToShow = this._sensors.slice(0, showCount);

    return sensorsToShow.map(entityId => {
      const state = this.hass.states[entityId];
      if (!state) return html``;

      const tipo = state.state;
      const attrs = state.attributes;
      const daysUntil = attrs.days_until;
      const date = new Date(attrs.date);
      const weekday = attrs.weekday;
      const icon = attrs.icon || 'mdi:recycle';
      const color = attrs.color || '#4CAF50';

      let daysText;
      if (daysUntil === 0) {
        daysText = translations.today;
      } else if (daysUntil === 1) {
        daysText = translations.tomorrow;
      } else {
        daysText = translations.days_until.replace('{}', daysUntil);
      }

      return html`
        <div class="collection" style="background-color: ${color}20;">
          <div class="collection-icon">
            <ha-icon icon="${icon}" style="color: ${color};"></ha-icon>
          </div>
          <div class="collection-info">
            <div class="collection-type">${tipo}</div>
            <div class="collection-date">${weekday}, ${date.toLocaleDateString(language)}</div>
          </div>
          <div class="days-until" style="background-color: ${color};">
            ${daysText}
          </div>
        </div>
      `;
    });
  }

  _getTranslations(language) {
    const translations = {
      it: {
        next_collection: "Prossimo conferimento",
        days_until: "tra {} giorni",
        tomorrow: "domani",
        today: "oggi",
      },
      en: {
        next_collection: "Next waste collection",
        days_until: "in {} days",
        tomorrow: "tomorrow",
        today: "today",
      },
    };

    return translations[language] || translations.en;
  }
}

customElements.define('raccolta-differenziata-card', RaccoltaDifferenziataCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "raccolta-differenziata-card",
  name: "Raccolta Differenziata Card",
  description: "Card per visualizzare i prossimi conferimenti della raccolta differenziata",
});