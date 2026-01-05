"""
Configuration for Paper Trading Forward Testing System
"""
import os
from pathlib import Path

# ============================================================================
# EXCHANGE SETTINGS
# ============================================================================
# Supported exchanges: 'binance', 'delta' (Delta Exchange India)
EXCHANGE = os.getenv('EXCHANGE', 'binance')  
SYMBOL = os.getenv('SYMBOL', 'ETH/USDT')  # Binance format: ETH/USDT, Delta: ETHUSD
TIMEFRAME = '3m'  # 3-minute candles

# Exchange-specific settings
EXCHANGE_CONFIG = {
    'binance': {
        'symbol': 'ETH/USDT',
        'testnet': False
    },
    'delta': {
        'symbol': 'ETHUSD',
        'api_url': 'https://api.india.delta.exchange'
    }
}

# ============================================================================
# TRADING PARAMETERS
# ============================================================================
INITIAL_CAPITAL = 100.0  # Starting virtual capital
RISK_PER_TRADE = 0.02  # 2% risk per trade
SLIPPAGE = 0.0005  # 0.05% slippage
COMMISSION = 0.0006  # 0.06% commission per trade

# ============================================================================
# STRATEGY PARAMETERS
# ============================================================================
EMA_PERIOD = 200  # EMA period for equity curve filter
HISTORICAL_DAYS = 365  # Days of historical data to bootstrap

# ============================================================================
# DATA PATHS
# ============================================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
STATE_DIR = BASE_DIR / 'state'

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)

# File paths
TRADES_LOG = LOGS_DIR / 'trades.csv'
EQUITY_LOG = LOGS_DIR / 'equity.csv'
SYSTEM_LOG = LOGS_DIR / 'system.log'
STATE_FILE = STATE_DIR / 'state.json'

# ============================================================================
# TELEGRAM SETTINGS (Optional)
# ============================================================================
TELEGRAM_ENABLED = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# ============================================================================
# SYSTEM SETTINGS
# ============================================================================
UPDATE_INTERVAL = 180  # Seconds between candle updates (3 minutes)
HEALTH_CHECK_PORT = int(os.getenv('PORT', 8080))  # For Railway health checks
MAX_RETRIES = 3  # Max retries for API calls
RETRY_DELAY = 5  # Seconds between retries

# ============================================================================
# LOGGING SETTINGS
# ============================================================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
