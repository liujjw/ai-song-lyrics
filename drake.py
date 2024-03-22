import lyricsgenius
genius = lyricsgenius.Genius("gEZ-F4U_Gs4PMM765ZCYPCoIfaYrygsNcQDvzAaKSRXodwmnTb8xsvyNNtpzaOc_")

artist = genius.search_album("For All The Dogs Scary Hours Edition", "Drake")
artist.save_lyrics()