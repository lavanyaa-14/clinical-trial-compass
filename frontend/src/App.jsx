import React, { useState } from 'react';
import PatientForm from './components/PatientForm';
import LoadingStepper from './components/LoadingStepper';
import ProfileCard from './components/ProfileCard';
import MatchCard from './components/MatchCard';
import { postMatch } from './api';

function App() {
  const [state, setState] = useState('form'); // 'form' | 'loading' | 'results'
  const [patientProfile, setPatientProfile] = useState(null);
  const [matches, setMatches] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async (profile) => {
    setState('loading');
    setError(null);
    setPatientProfile(profile);

    try {
      const response = await postMatch(profile);
      setMatches(response.matches);
      setState('results');
    } catch (err) {
      console.error('Error fetching matches:', err);
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Failed to fetch matches. Please try again.'
      );
      setState('form');
    }
  };

  const handleNewSearch = () => {
    setState('form');
    setPatientProfile(null);
    setMatches([]);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {state === 'form' && (
        <>
          <PatientForm onSubmit={handleSubmit} isLoading={state === 'loading'} />
          {error && (
            <div className="max-w-2xl mx-auto mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          )}
        </>
      )}

      {state === 'loading' && <LoadingStepper />}

      {state === 'results' && patientProfile && (
        <div className="min-h-screen bg-gradient-to-b from-red-50 to-white p-4">
          <div className="max-w-3xl mx-auto">
            <button
              onClick={handleNewSearch}
              className="mb-6 px-4 py-2 bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium rounded-lg transition"
            >
              ← Search Again
            </button>

            <ProfileCard profile={patientProfile} />

            <div className="bg-white rounded-lg shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Top Matching Trials ({matches.length})
              </h2>

              {matches.length === 0 ? (
                <p className="text-gray-600">No matching trials found.</p>
              ) : (
                <div className="space-y-4">
                  {matches.map((match) => (
                    <MatchCard key={match.nct_id} match={match} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
