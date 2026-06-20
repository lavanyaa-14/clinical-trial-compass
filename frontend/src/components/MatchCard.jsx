import React, { useState } from 'react';
import CaveatBadge from './CaveatBadge';

const MatchCard = ({ match }) => {
  const [expandedCriteria, setExpandedCriteria] = useState(false);

  const getScoreBadgeColor = () => {
    if (match.match_score >= 75) return 'bg-green-100 text-green-800 border-green-300';
    if (match.match_score >= 50) return 'bg-amber-100 text-amber-800 border-amber-300';
    return 'bg-red-100 text-red-800 border-red-300';
  };

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'meets':
        return 'bg-green-100 text-green-800';
      case 'does_not_meet':
        return 'bg-red-100 text-red-800';
      case 'unclear':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatVerdictLabel = (verdict) => {
    switch (verdict) {
      case 'meets':
        return '✓ Meets';
      case 'does_not_meet':
        return '✗ Does Not Meet';
      case 'unclear':
        return '? Unclear';
      default:
        return verdict;
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mb-4 shadow-sm hover:shadow-md transition">
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 mb-1">{match.title}</h3>
          <a
            href={match.trial_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-red-600 hover:underline font-medium"
          >
            {match.nct_id}
          </a>
        </div>
        <div className="flex gap-2 ml-4">
          <span className="text-xs font-semibold px-3 py-1 rounded border bg-purple-100 text-purple-800 border-purple-300">
            Phase {match.phase}
          </span>
          <span
            className={`text-lg font-bold px-3 py-1 rounded border ${getScoreBadgeColor()}`}
          >
            {match.match_score}%
          </span>
        </div>
      </div>

      {/* Conditions */}
      <div className="mb-4">
        <p className="text-xs text-gray-500 font-semibold uppercase mb-1">Conditions</p>
        <div className="flex flex-wrap gap-2">
          {match.conditions.map((condition, idx) => (
            <span
              key={idx}
              className="inline-block text-xs bg-red-100 text-red-800 px-2 py-1 rounded"
            >
              {condition}
            </span>
          ))}
        </div>
      </div>

      {/* Match narrative */}
      <p className="text-gray-700 text-sm mb-4 leading-relaxed">{match.match_narrative}</p>

      {/* Expandable criteria */}
      <div>
        <button
          onClick={() => setExpandedCriteria(!expandedCriteria)}
          className="text-sm font-medium text-red-600 hover:text-red-800 mb-3 flex items-center gap-2"
        >
          {expandedCriteria ? '▼' : '▶'} View criteria breakdown
        </button>

        {expandedCriteria && match.criterion_verdicts && match.criterion_verdicts.length > 0 && (
          <div className="mb-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-300">
                  <th className="text-left px-3 py-2 font-semibold text-gray-700">
                    Criterion
                  </th>
                  <th className="text-left px-3 py-2 font-semibold text-gray-700">Verdict</th>
                  <th className="text-left px-3 py-2 font-semibold text-gray-700">Reason</th>
                </tr>
              </thead>
              <tbody>
                {match.criterion_verdicts.map((cv, idx) => (
                  <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="px-3 py-2 text-gray-700">{cv.criterion}</td>
                    <td className="px-3 py-2">
                      <span className={`inline-block text-xs font-semibold px-2 py-1 rounded ${getVerdictColor(cv.verdict)}`}>
                        {formatVerdictLabel(cv.verdict)}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-gray-600">{cv.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Caveats */}
      <CaveatBadge caveats={match.caveats} />
    </div>
  );
};

export default MatchCard;
