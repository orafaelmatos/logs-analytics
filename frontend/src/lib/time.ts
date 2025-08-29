export const brazilTimeISOString = (date: Date = new Date()) => {
  // Brazil offset in hours (normally UTC-3, adjust for DST if needed)
  const BRAZIL_OFFSET = -3; 
  const utc = date.getTime() + date.getTimezoneOffset() * 60000; // UTC timestamp
  const brazilDate = new Date(utc + BRAZIL_OFFSET * 3600 * 1000);
  return brazilDate.toISOString().split('.')[0]; // remove milliseconds
};