truncate table public."SongParts";

select
  *
from
  public."Songs"
where
  lyrics ilike '%blue handkerchiefs%';

  delete from public."Songs"
where
  artist = 'Drake';

delete from public."SongParts"
where
  song_id in (
    select
      id
    from
      public."Songs"
    where
      artist = 'Drake'
  );

drop function if exists get_songs_by_artist;
create function get_songs_by_artist (parameter varchar)
RETURNS TABLE(column1 integer, column2 varchar) AS
$$
BEGIN
  return query  select
                  s.title as song_title,
                  sp.lyrics,
                  sp.keyphrases
                from
                  Public."Songs" s
                  join Public."SongParts" sp on s.id = sp.song_id
                where
                  s.artist = parameter
                limit
                  100
                offset
                  0;
END;
$$
language plpgsql volatile;

drop view if exists songsbyartist_chorus;

create view
  songsbyartist_chorus as
select
  s.title as song_title,
  sp.lyrics,
  sp.keyphrases,
  s.artist
from
  Public."Songs" s
  join Public."SongParts" sp on s.id = sp.song_id
where
  sp.part_type = 'Chorus'
order by
  s.title;

drop view if exists songsbyartist_outro;

create view
  songsbyartist_outro as
select
  s.title as song_title,
  sp.lyrics,
  sp.keyphrases,
  s.artist
from
  Public."Songs" s
  join Public."SongParts" sp on s.id = sp.song_id
where
  sp.part_type = 'Outro'
order by
  s.title;

drop view if exists songsbyartist;

create view
  songsbyartist as
select
  s.title as song_title,
  sp.lyrics,
  sp.keyphrases,
  s.artist
from
  Public."Songs" s
  join Public."SongParts" sp on s.id = sp.song_id
order by
  s.title
-- limit
--   100
-- offset
--   0;

create view uniqueartists as
  select distinct
    artist
  from
    public."Songs";

  drop view if exists songsbyartist_verse;

create view
  songsbyartist_verse as
select
  s.title as song_title,
  sp.lyrics,
  sp.keyphrases,
  s.artist
from
  Public."Songs" s
  join Public."SongParts" sp on s.id = sp.song_id
where
  sp.part_type = 'Verse'
order by
  s.title;

drop view if exists songsbyartist_intro;

create view
  songsbyartist_intro as
select
  s.title as song_title,
  sp.lyrics,
  sp.keyphrases,
  s.artist
from
  Public."Songs" s
  join Public."SongParts" sp on s.id = sp.song_id
where
  sp.part_type = 'Intro'
order by
  s.title;