// GitHubPopup.js
import React, { useState } from 'react';
import logo from './assets/logo2.png';

const GitHubPopup = ({ show, onClose, onGitHubSubmit, gitHubUrl, setGitHubUrl }) => {
  const [error, setError] = useState(null);

  const validateGitHubUrl = (url) => {
    const regex = /https:\/\/github\.com\/([^/]+)\/([^/.]+)/;
    return regex.test(url);
  };

  const handleSubmit = () => {
    if (validateGitHubUrl(gitHubUrl)) {
      // Valid GitHub URL, proceed with the submit function
      onGitHubSubmit();
    } else {
      // Invalid GitHub URL, show an error
      setError('Invalid GitHub Repository URL');
    }
  };

  return (
    show && (
      <div className='darkPopupContainer'>
        <img src={logo} alt='Logo' className='logoImage' />
        <div className='darkPopup'>
          <div className='popupContent'>
            <input
              type='text'
              placeholder='GitHub Repository URL'
              value={gitHubUrl}
              onChange={(e) => setGitHubUrl(e.target.value)}
            />
            <button onClick={handleSubmit}>Submit</button>
            <button onClick={onClose}>Cancel</button>
            {error && <p className="error">{error}</p>}
          </div>
        </div>
      </div>
    )
  );
};

export default GitHubPopup;
