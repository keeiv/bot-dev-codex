# BOT. feature map

Where each feature lives. Cogs are under `src/cogs/`, services under `src/services/`, messages under `src/locales/`. Run `/scan` for the current file list.

| Feature | Cog | Service and helpers |
| --- | --- | --- |
| Anti-spam, raid lockdown and restore | `features/anti_spam.py` | `src/utils/anti_spam.py` |
| Global bans across servers | `core/global_ban.py`, `global_ban` in `src/bot.py` | `global_ban_service.py` |
| Blacklist (local, API, Mori.black) and appeals | `core/blacklist.py` | `blacklist_service.py`, `src/utils/blacklist_manager.py` |
| Message edit and delete log | `core/message_logger.py` | `message_log_service.py`, `message_log_store.py` (tables) |
| Audit log | `core/audit_log.py` | `audit_log_service.py` |
| Reports and moderation actions | `core/report.py` | `report_service.py` |
| Settings, language, appearance | `core/settings.py`, `core/language.py`, `core/bot_appearance.py` | `language_service.py`, `appearance_service.py` |
| Errors, maintenance, performance | `core/error_handler.py`, `core/system_maintenance.py`, `core/performance_monitor.py` | |
| Dashboard API for the website | `core/dashboard_api.py` | `dashboard_service.py`, `dashboard_account.py`, `dashboard_checks.py`, `dashboard_health.py`, `dashboard_history.py` |
| Welcome messages and auto roles | `features/management.py` | `management_service.py` |
| Giveaways (resume mid-draw) | `features/giveaway.py` | `giveaway_service.py` |
| Tickets | `features/ticket.py` | `ticket_service.py` |
| Temporary voice channels | `features/temp_voice.py` | `temp_voice_service.py` |
| Petitions | `features/petition.py` | `petition_service.py` |
| Age guard | `features/age_guard.py` | `age_guard_service.py` |
| Achievements | `features/achievements.py` | `achievement_service.py` |
| User and server info | `features/user_server_info.py` | |
| Translation | `features/translate.py` | |
| GitHub repository watch | `features/github_watch.py` | `github_watch_service.py`, `services/github/` |
| AI chat | `features/ai_chat.py` | `ai_chat_service.py`, `ai_cli.py`, `ai_game_profile.py` |
| HoYoLAB / Miyoushe | `features/genshin_cog.py` | `genshin_service.py` |
| Arknights: Endfield | `features/endfield_cog.py` | `endfield_service.py`, `skport_client.py` |
| File tools and NovaGrid nodes | `features/file_tools.py` | `file_tools.py`, `tool_*.py`, `novagrid.py` |
| AI image review node | | `moderation_*.py` |
| Companion pets | `games/pet.py` | `pet_service.py`, `pet_rules.py`, `pet_art.py`, `pet_card.py` |
| Rust Anchor Station activity | `games/station.py` (launches the Discord activity; the games live in the website repository) | |
| Terminal control panel | `src/control_panel/` | `labels.py` names stored fields in Chinese |

Shared plumbing in `src/utils/`: `document_store.py` and `mysql_compat.py` (storage), `storage_worker.py` (`run_storage`), `i18n.py` and `lang_context.py` (language), `localized_ui.py` (views), `command_sync.py` and `command_translator.py` (commands), `event_errors.py` (listener storage outages).
