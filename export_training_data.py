from pathlib import Path

import pandas as pd

from database import get_connection, get_training_dataframe, init_db


def main():
    init_db()

    export_folder = Path("exports")
    export_folder.mkdir(exist_ok=True)

    with get_connection() as connection:
        all_sessions = pd.read_sql_query(
            """
            SELECT *
            FROM sessions
            WHERE completed_at IS NOT NULL
            ORDER BY completed_at DESC
            """,
            connection,
        )

        profile_counts = pd.read_sql_query(
            """
            SELECT
                final_profile_label,
                COUNT(*) AS total
            FROM sessions
            WHERE completed_at IS NOT NULL
            GROUP BY final_profile_label
            ORDER BY total DESC, final_profile_label ASC
            """,
            connection,
        )

    training_rows = get_training_dataframe(min_success_score=3.0)

    all_sessions_path = export_folder / "all_completed_sessions.csv"
    training_rows_path = export_folder / "training_rows.csv"
    profile_counts_path = export_folder / "profile_counts.csv"

    all_sessions.to_csv(all_sessions_path, index=False)
    training_rows.to_csv(training_rows_path, index=False)
    profile_counts.to_csv(profile_counts_path, index=False)

    print("\nSaved files:")
    print(all_sessions_path.resolve())
    print(training_rows_path.resolve())
    print(profile_counts_path.resolve())

    print("\nProfile counts:")
    if profile_counts.empty:
        print("No completed sessions found yet.")
    else:
        print(profile_counts.to_string(index=False))

    print("\nTraining rows:")
    print(len(training_rows))


if __name__ == "__main__":
    main()