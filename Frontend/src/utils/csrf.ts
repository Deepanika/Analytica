/**
 * Get a cookie value by name.
 * Typically used to retrieve CSRF tokens for Django-secured APIs.
 * 
 * @param name - The name of the cookie to retrieve.
 * @returns The cookie value if found, otherwise null.
 */
export const getCookie = (name: string): string | null => {
    let cookieValue: string | null = null;
  
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
  
        // Check if this cookie matches the requested name
        if (cookie.substring(0, name.length + 1) === `${name}=`) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
  
    return cookieValue;
  };
  